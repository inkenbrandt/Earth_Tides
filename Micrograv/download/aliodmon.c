/*
 * Monitor an Aliod-equipped meter directly.
 *
 * BEWARE PIN 9 ON THE ALIOD - it has +5V instead of
 * ground; use included null-modem which has no pin 9!
 *
 */
#include <stdio.h>
#include <stdlib.h>
#include <termios.h>
#include <unistd.h>
#include <sys/time.h>
#include <fcntl.h>
#include <string.h>
#include <errno.h>
#include <ctype.h>
#include <time.h>

char *version = "1.0special";

void usage(void);
void initSerialPort(int handle, int baud);
void makeraw(struct termios *termios_p);
int main(int argc, char *argv[]);
int emptyRecord(char *rec);

void usage(void)
{
  fprintf(stderr, "usage:\n  aliodmon [options] counterValue outputfile\n");
  fprintf(stderr, "options:\n");
  fprintf(stderr, "  -p PORT\tSet the serial port to device PORT; full path\n");
  fprintf(stderr, "  -b BAUD\tSet the serial port baud rate\n");
  fprintf(stderr, "\n");
  fprintf(stderr, "Aliod is always 8 bits, no parity\n");
}

void initSerialPort(int handle, int baud)
{
  struct termios ios;

  /* get the terminal attributes */
  if(tcgetattr(handle, &ios) < 0) {
    fprintf(stderr,"Can't get terminal attributes.\n");
    exit(1);
    }
  if(cfsetispeed(&ios, baud) < 0) {
    fprintf(stderr,"Can't set input baud rate.\n");
    exit(1);
    }
  if(cfsetospeed(&ios, baud) < 0) {
    fprintf(stderr,"Can't set output baud rate.\n");
    exit(1);
    }
  makeraw(&ios);

  /* set the terminal attributes */
  if(tcsetattr(handle, TCSANOW, &ios) < 0) {
    fprintf(stderr,"Can't set port attributes.\n");
    exit(1);
    }
}

void makeraw(struct termios *termios_p)
{
  /* replicate the cfmakeraw() from linux */
  termios_p->c_iflag &= ~(IGNBRK|BRKINT|PARMRK|ISTRIP|INLCR|IGNCR|ICRNL|IXON);
  termios_p->c_oflag &= ~OPOST;
  termios_p->c_lflag &= ~(ECHO|ECHONL|ICANON|ISIG|IEXTEN);
  termios_p->c_cflag &= ~(CSIZE|PARENB);
  termios_p->c_cflag |= CS8;
}


int main(int argc, char *argv[])
{
  int portHandle;
  int br, baud;

  int nb;
  long nrec, lines;

  char *record, input[1024], *bufptr;
  char string[80], bstr[10];
  char outstr[1024], counter[25], timestr[22];
  int offset, i;
  char *portName = "/dev/ttyS0";
  char option, keybuf[80];
  const char *optstring = "p:b:h?";

  unsigned char newRecord, inHeader, run;

  time_t now;
  struct timeval tv;
  struct timezone tz;

  FILE *outfp;

  if(argc < 3) {
    usage();
    exit(1);
    }

  printf("Aliod Monitor Program\n");
  printf(" Version %s\n", version);
  /* deal with command-line arguments */
  baud = B4800; strcpy(bstr, "4800");
  while((option = getopt(argc, argv, optstring)) != -1) {
    switch(option) {
      case '?': /* unknown option */
        usage();
        exit(1);
        break;
      case 'p': /* set the port name */
	free(portName);
	if((portName = malloc(strlen(optarg))) == NULL) {
	  fprintf(stderr, "Cannot allocate memory for port name.\n");
	  exit(1);
	  }
	strcpy(portName, optarg);
	break;
      case 'b': /* set baud rate */
        br = atoi(optarg);
        switch(br) {
          case 300:  baud=B300 ; strcpy(bstr, "300"); break;
          case 1200: baud=B1200; strcpy(bstr, "1200"); break;
          case 2400: baud=B2400; strcpy(bstr, "2400"); break;
          case 4800: baud=B4800; strcpy(bstr, "4800"); break;
          case 9600: baud=B9600; strcpy(bstr, "9600"); break;
          case 19200: baud=B19200; strcpy(bstr, "19200"); break;
          default: baud = B2400; strcpy(bstr, "2400"); break;
          }
        break;
      case 'h': /* get help */
        usage();
        exit(1);
        break;
      default:
        usage();
        exit(1);
        break;
      }
    }

  printf("Using port %s at baud %s.\n", portName, bstr);

  /* copy off counter value */
  strncpy(counter, argv[optind], 25);
  optind++;

  /* open the serial port */
  if((portHandle = open(portName, O_RDONLY)) < 0) {
    fprintf(stderr, "Cannot open port.\n");
    exit(1);
    }

  /* setup the serial port */
  initSerialPort(portHandle, baud);

  /* open output data file, truncating it */
  if((outfp = fopen(argv[optind], "wt")) == NULL) {
    fprintf(stderr, "Cannot open output file %s for write.\n", argv[optind]);
    exit(1);
    }

  /* read records until told to stop */
  if((record = malloc(1024*sizeof(char))) == NULL) {
    fprintf(stderr, "Cannot allocate memory for record buffer.\n");
    exit(1);
    }
  memset(record, 0, 1023);
  bufptr = record;
  nrec = 0;
  lines = 0;
  offset = 0;
  newRecord = inHeader = 0;
  run = 1;
  printf("LINE   RECORD \n");
  printf("---- ----------\n");
  while(run) {
    if((nb = read(portHandle, bufptr, 1024-offset)) == -1) {
      if(errno == EAGAIN) { /* do nothing */
        }
      else {
        perror("main");
        }
      continue;
      }
    offset += nb;
    if(offset > 1023) {
      offset = 0;
      }
    for(i=0; i<offset; i++) {
      if(record[i] == '\n') {
        record[i] = 0;
        strcpy(input, record);
        strcpy(record, &record[i+1]);
        offset -= strlen(input)+1;
        newRecord = 1;
        break;
        }
      /* convert control chars to something innocuous */
      if(record[i] < 32) {
        record[i] = ' ';
        }
      }

    bufptr = record+offset*sizeof(char);
    if(newRecord) {
      newRecord = 0;
      lines++;
      if(emptyRecord(input)) {
	nrec++;
	/*now = time(NULL);*/
	gettimeofday(&tv, &tz);
	now = tv.tv_sec;
	strftime(timestr, 21, "%Y-%m-%d,%H:%M:%S", gmtime(&now));
	snprintf(outstr, 1023, "%s.%06d,%s,%s", timestr, tv.tv_usec, &input[3], counter);
	fprintf(outfp, "%s\n", outstr);
	fflush(outfp);
	printf("%4d:%s\n", nrec, outstr);
        }
      }
    }

  fclose(outfp);
  close(portHandle);
  printf("Downloaded %d records in %d lines.\n", nrec, lines);
  exit(0);
}

int emptyRecord(char *rec)
{
  int i;

  i=0;
  while(rec[i] != 0) {
    if(isalnum(rec[i])) return(1);
    i++;
    }
  return(0);
}
