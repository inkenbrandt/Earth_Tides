/**
  * Parse a DC v7.5 file for useful info
  *
  * Paul Gettings, University of Utah, Dep't of Geology & Geophysics
  * July 2001
  *
  * compile with:
  *   g++ -o parseDC parseDC.cpp
  */
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h> //getopt

// bits to indicate desired records
#define HEADER_REC	0x0000000000000001L
#define POSITION_REC	0x0000000000000002L
#define VECTOR_REC	0x0000000000000004L
#define QC1_REC		0x0000000000000008L
#define QC2_REC		0x0000000000000010L
#define QC3_REC		0x0000000000000020L
#define JOB_REC		0x0000000000000040L
#define NOTE_REC	0x0000000000000080L

// function prototypes
char *parseHeader(char *buf);
char *parseJob(char *buf);
char *parseNote(char *buf);
char *parsePosition(char *buf);
char *parseVector(char *buf);
char *parseQC1(char *buf);
char *parseQC2(char *buf);
char *parseQC3(char *buf);
int subString(char *out, char *in, unsigned start, unsigned len);
char *getDerivation(char *in);
char *getGPSMethod(char code);
char *getClassification(char code);
char *getAngleUnit(char code);
char *getDistanceUnit(char code);
char *getPressureUnit(char code);
char *getTemperatureUnit(char code);
char *getCoordOrder(char code);
char *getAngleDirection(char code);
void usage(void);

void usage(void)
{
  fprintf(stderr, "usage: parseDC [options] DC_file\n");
  fprintf(stderr, "options:\n");
  fprintf(stderr, " -h	print header   records\n");
  fprintf(stderr, " -p	      position\n");
  fprintf(stderr, " -v	      vector\n");
  fprintf(stderr, " -1	      QC1\n");
  fprintf(stderr, " -2	      QC2\n");
  fprintf(stderr, " -3	      QC3\n");
  fprintf(stderr, " -j	      Job\n");
  fprintf(stderr, " -n	      Note\n");
}


int main(int argc, char *argv[])
{
  unsigned long flags = 0;
  const char *options="hpv123jn?";
  char buf[1024], opt;
  FILE *fp;

  if(argc < 2) {
    usage();
    exit(1);
    }

  while((opt = getopt(argc, argv, options)) != -1) {
    switch(opt) {
      case 'h': flags |= HEADER_REC;
      		break;
      case 'p': flags |= POSITION_REC;
      		break;
      case 'v': flags |= VECTOR_REC;
      		break;
      case '1': flags |= QC1_REC;
      		break;
      case '2': flags |= QC2_REC;
      		break;
      case '3': flags |= QC3_REC;
      		break;
      case 'j': flags |= JOB_REC;
      		break;
      case 'n': flags |= NOTE_REC;
      		break;
      case '?': usage();
      		exit(1);
      		break;
      }
    }
  if((fp = fopen(argv[optind], "rt")) == NULL) {
    fprintf(stderr, "cannot open %s for read.\n", argv[optind]);
    exit(1);
    }
#ifdef DEBUG
  fprintf(stderr, "flags: %0lx\n", flags);
#endif

  // read the file and extract records we want
  while(!feof(fp)) {
    fgets(buf, 1024, fp);
    if(feof(fp)) continue;

    // handle the record type
    switch(buf[0]) {
      case '0':
        switch(buf[1]) {
          case '0': //HEADER
          	if(flags & HEADER_REC) {
		  printf("%s\n", parseHeader(buf));
		  }
          	break;
          case '2': //STATION
          case '4': //COLLIMATION
          case '5': //ATMOSPHERE
          case '7': //BACKBEARING
          default:  //UNKNOWN
          	break;
	  }
	break;
      case '1':
        switch(buf[1]) {
          case '0': //JOB
          	if(flags & JOB_REC)
		  printf("%s\n", parseJob(buf));
          	break;
          case '3': //NOTE
          	if(flags & NOTE_REC)
		  printf("%s\n", parseNote(buf));
          	break;
          default:  //OTHER
          	break;
          }
	break;
      case '2':
      case '3':
      case '4':
      	break;
      case '5':
        switch(buf[1]) {
          case '9': //QC2
          	if(flags & QC2_REC)
		  printf("%s\n", parseQC2(buf));
	  default:  //OTHER
	  	break;
	  }
	break;
      case '6':
        switch(buf[1]) {
          case '0': //QC3
           	if(flags & QC3_REC)
           	  printf("%s\n", parseQC3(buf));
           	  break;
          case '2': //QC1
           	if(flags & QC1_REC)
           	  printf("%s\n", parseQC1(buf));
           	  break;
          case '6': //GPS POSITION
           	if(flags & POSITION_REC)
           	  printf("%s\n", parsePosition(buf));
           	  break;
          case '7': //GPS VECTOR
           	if(flags & VECTOR_REC)
           	  printf("%s\n", parseVector(buf));
           	  break;
          default:  //OTHER
          	break;
	  }
	break;
      default:
      	break;
      }
    }
  fclose(fp);
  exit(0);
}

char *parseHeader(char *buf)
{
  static char out[1024];
  char *derivation, version[17], serial[5], time[17];
  char *angle, *distance, *temp, *pressure, *order, *angled;

  // parse the record into fields
  derivation = getDerivation(buf);
  subString(version, buf, 4, 16);
  subString(serial, buf, 20, 4);
  subString(time, buf, 24, 16);
  angle = getAngleUnit(buf[40]);
  distance = getDistanceUnit(buf[41]);
  pressure = getPressureUnit(buf[42]);
  temp = getTemperatureUnit(buf[43]);
  order = getCoordOrder(buf[44]);
  angled = getAngleDirection(buf[45]);

  // create output string
  snprintf(out, 1023,
   "HEADER from %s Version:%16s Serial#:%4s Timestamp:%16s units: %s %s %s %s %s %s",
   derivation, version, serial, time, angle, distance, pressure, temp, order, angled);
  return(out);
}

char *parseJob(char *buf)
{
  static char out[1024];
  char name[17];

  subString(name, buf, 4, 16);
  snprintf(out, 1023, "JOB name: %s", name);
  return(out);
}

char *parseNote(char *buf)
{
  static char out[1024];
  char note[61];

  subString(note, buf, 4, 60);
  snprintf(out, 1023, "NOTE %s", note);
  return(out);
}

char *parsePosition(char *buf)
{
  static char out[1024];
  char name[17], lat[17], lon[17], z[17], feature[17], hprec[17], vprec[17];
  char *method, *clas, *derivation;
  double dh, dv;

  subString(name, buf,  4, 16);
  subString(lat , buf, 20, 16);
  subString(lon , buf, 36, 16);
  subString(z   , buf, 52, 16);
  subString(feature,buf,68,16);
  subString(hprec,buf, 86, 16);
  subString(vprec,buf, 102,16);
  derivation = getDerivation(buf);
  method = getGPSMethod(buf[84]);
  clas = getClassification(buf[85]);

  dh = atof(hprec);
  dv = atof(vprec);

  snprintf(out, 1023, "POS from %s for %s ( %s , %s , %s ) +- (%.3lf, %.3lf) method:%s class:%s feat:[%s]",
    derivation, name, lat, lon, z, dh, dv, method, clas, feature);
  return(out);
}

char *parseVector(char *buf)
{
  static char out[1024];
  char name[17], x[17], y[17], z[17], feature[17], hprec[17], vprec[17];
  char *method, *clas, *derivation;
  double dh, dv;

  subString(name, buf,  4, 16);
  subString(x   , buf, 20, 16);
  subString(y   , buf, 36, 16);
  subString(z   , buf, 52, 16);
  subString(feature,buf,68,16);
  subString(hprec,buf, 86, 16);
  subString(vprec,buf, 102,16);
  derivation = getDerivation(buf);
  method = getGPSMethod(buf[84]);
  clas = getClassification(buf[85]);

  dh = atof(hprec);
  dv = atof(vprec);

  snprintf(out, 1023, "VEC from %s for %s ( %s , %s , %s ) +- (%.3lg, %.3lg) method:%s class:%s feat:[%s]",
    derivation, name, x, y, z, dh, dv, method, clas, feature);
  return(out);
}

char *parseQC1(char *buf)
{
  // XXX - fixme
  return(parseQC2(buf));
}

char *parseQC2(char *buf)
{
  // XXX - fixme
  return(parseQC3(buf));
}

char *parseQC3(char *buf)
{
  // XXX - fixme
  return("QC records not yet implemented");
}

int subString(char *out, char *in, unsigned start, unsigned len)
{
  unsigned long i;
  for(i=0; i<len; i++)
    out[i] = in[i+start];
  out[len] = '\0';
  return(i);
}

char *getDerivation(char *in)
{
  // XXX - should be a switch/case to map code to meaningful strings
  static char d[3];
  d[0] = in[2];
  d[1] = in[3];
  d[2] = '\0';
  return(d);
}

char *getGPSMethod(char code)
{
  switch(code) {
    case '1': return("User Input");
    case '2': return("Autonomous");
    case '3': return("RTK Float/RTCM");
    case '4': return("RTK Fixed");
    case '5': return("Copied Pt");
    case '6': return("RTCM Code");
    case '7': return("WAAS");
    default : return("Unknown");
    }
}

char *getClassification(char code)
{
  switch(code) {
    case '1': return("Normal");
    case '2': return("Control");
    case '3': return("AsBuilt");
    case '4': return("Check");
    case '5': return("BackSight");
    case '6': return("Del. Normal");
    case '7': return("Del. Control");
    case '8': return("Del. AsBuilt");
    case '9': return("Del. Check");
    case ':': return("Del. BackSight");
    default : return("Unknown");
    }
}

char *getAngleUnit(char code)
{
  switch(code) {
    case '1': return("Degrees");
    case '2': return("Grads");
    case '3': return("Mils");
    default:  return("Unknown");
    }
}

char *getDistanceUnit(char code)
{
  switch(code) {
    case '1': return("Meters");
    case '2': return("Feet");
    case '3': return("US Feet");
    default : return("Unknown");
    }
}

char *getPressureUnit(char code)
{
  switch(code) {
    case '1': return("mm Hg");
    case '2': return("in Hg");
    case '3': return("mbar");
    default : return("Unknown");
    }
}

char *getTemperatureUnit(char code)
{
  switch(code) {
    case '1': return("C");
    case '2': return("F");
    default : return("Unknown");
    }
}

char *getCoordOrder(char code)
{
  switch(code) {
    case '1': return("North-East-Elev");
    case '2': return("East-North-Elev");
    case '3': return("Y-X-Z");
    default : return("Unknown");
    }
}

char *getAngleDirection(char code)
{
  switch(code) {
    case '1': return("CW");
    case '2': return("CCW");
    default : return("Unknown");
    }
}
