/*
 * Download a CG-3(M) meter or GravLog-running Palm, or something else...
 * Paul Gettings
 * Dep't of Geology & Geophysics, U of Utah
 *
 * Released under the GPL (see www.gnu.org). Have fun.
 *
 * compile with:
 * gcc -o download download.c kb.c
 *
 * Theory of Operation:
 * Opens a serial port, and listens for anything on it.  Buffers until
 * a newline, which it interprets as the end of a record.  The record is
 * then written to the output file, after control characters are replaced
 * with spaces.  When it receives a ^S (decimal 19), it stops.  If you
 * press 'Q' the program stops, which is needed for GravLog downloads;
 * case is important.
 * 
 * Records are checked to watch for the start and stop of a header
 * block (CG-3 only); the number of records is counted, excluding
 * header lines.
 *
 * Prints records as they are received, with the current line number.
 * Note that even though only the first 74 characters of a record are
 * printed, the whole record is stored to disk.
 * 
 * Assumes serial settings of 8 bits, no parity.  Baud is selectable.
 * Default baud rate is 2400, but must select 4800 for GravLog!
 */
#include <stdio.h>
#include <stdlib.h>
#include <termios.h>
#include <unistd.h>
#include <fcntl.h>
#include <string.h>
#include <errno.h>
#include <ctype.h>
#include "kb.h"

char *version = "1.5";

void usage(void);
void initSerialPort(int handle, int baud);
void makeraw(struct termios *termios_p);
int main(int argc, char *argv[]);
int emptyRecord(char *rec);

void usage(void)
{
  fprintf(stderr, "usage:\n  download [options] outputfile\n");
  fprintf(stderr, "options:\n");
  fprintf(stderr, "  -p PORT\tSet the serial port to device PORT; full path\n");
  fprintf(stderr, "  -b BAUD\tSet the serial port baud rate; default is 2400\n");
  fprintf(stderr, "\n");
  fprintf(stderr, "Device must be set to 8 bits, no parity\n");
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
  int offset, i;
  unsigned binaryFlag=0;
  char *portName = "/dev/ttyS0";
  char option, keybuf[80];
  const char *optstring = "p:b:h?B";

  unsigned char newRecord, inHeader, run;

  FILE *outfp;

  if(argc < 2) {
    usage();
    exit(1);
    }

  printf("Gravity Download Program\n");
  printf(" Version %s\n", version);
  /* deal with command-line arguments */
  baud = B2400; strcpy(bstr, "2400");
  while((option = getopt(argc, argv, optstring)) != -1) {
    switch(option) {
      case '?': /* unknown option */
        usage();
        exit(1);
        break;
      case 'p': /* set the port name */
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
          case 38400: baud=B38400; strcpy(bstr, "38400"); break;
          case 57600: baud=B57600; strcpy(bstr, "57600"); break;
          default: baud = B2400; strcpy(bstr, "2400"); break;
          }
        break;
      case 'h': /* get help */
        usage();
        exit(1);
        break;
      case 'B': /* binary download */
        binaryFlag = 1;
        break;
      default:
        usage();
        exit(1);
        break;
      }
    }

  printf("Using port %s at baud %s.\n", portName, bstr);

  /* open the serial port */
  if((portHandle = open(portName, O_RDONLY)) < 0) {
    fprintf(stderr, "Cannot open port.\n");
    exit(1);
    }

  /* setup the serial port */
  initSerialPort(portHandle, baud);

  /* setup the terminal for nonblocking keyboard */
/*  kb_nonblock(1);
*/
  /* open output data file, appending to it */
  if((outfp = fopen(argv[optind], "at")) == NULL) {
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
  memset(string, 0, 80); /* clear print buffer */
  printf("LINE    DATA\n");
  printf("---- ----------\n");
  while(run) {
    /* read the serial port */
    if((nb = read(portHandle, bufptr, 1024-offset)) == -1) {
      if(errno == EAGAIN) { /* do nothing */
        }
      else {
        perror("main");
        }
      continue;
      }
    offset += nb;

    if(binaryFlag) { /* binary input! */
      for(i=0; i<offset; i++) {
	fprintf(outfp, "%c", record[i]);
	printf("[%c]", record[i]);
	}
      fflush(outfp);
      printf("\n");
      offset = 0;
      }
    else {
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
	if(record[i] == 19) { /* 19 is ^S == EOF */
	  run = 0;
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
	fprintf(outfp, "%s\n", input);
	if(!strncmp(input, "--", 2)) {
	  inHeader = !inHeader;
	  if(!inHeader) nrec--;
	  }
	else if(!inHeader) {
	  if(emptyRecord(input))
	    nrec++;
	  }
	strncpy(string, input, 74);
	printf("%4d:%s\n", lines, string);
	}
      fflush(outfp);
      }
    }

  fclose(outfp);
  close(portHandle);
  printf("Downloaded %d records in %d lines.\n", nrec, lines);
  /* reset the terminal */
/*  kb_nonblock(0); */
  exit(0);
}

int emptyRecord(char *rec)
{
  int i;

  i = 0;
  while(rec[i] != '\0') {
    if(isalnum(rec[i]))
      return(1);
    i++;
    }
  return(0);
}

