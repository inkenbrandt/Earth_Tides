/*
 * tamMain.c - Front-end driver for Tamura's ETC code in tamura.c/.h
 *
 * Computes a full day of corrections, at 1-minute intervals, and
 * prints in a table
 *
 * Compile with:
 *   gcc -o tamMain tamMain.c tamura.c -lm
 */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "tamura.h"

int main(int argc, char *argv[])
{
  int yr, mo, day, hr;
  int i, j, nc;
  double elevation, lat, lon, latsec, lonsec;
  double C;

  if(argc < 7) {
    printf("usage: %s <lat> <lon> <elevation> <year> <month> <day>\n", argv[0]);
    printf("where lat/lon are in decimal degrees, positive north/east;\n");
    printf("      elevation in meters;\n");
    printf("      year is 4 digits, month is 1-12, and day is 1-31 in month\n");
    printf("      output is GMT time and correction.\n");
    exit(0);
    }
  /* usage: lat lon elevation jul_day */
  lat = atof(argv[1]);
  lon = atof(argv[2]);
  elevation = atof(argv[3]);
  yr = atoi(argv[4]);
  mo = atoi(argv[5]);
  day = atoi(argv[6]);

  // get 7 columns per page, each column can hold 1 hour in 1-min
  // increments; so, compute each page at a time
  nc = 7;
  hr = 0; // start at midnight
  while(hr < 24) {
    for(i=0; i<nc-1; i++) {
      printf("HR:MN  ETC| ");
      }
    printf("HR:MN  ETC");
    printf("\n");
    for(i=0; i<nc-1; i++) {
      printf("-----  ---| ");
      }
    printf("-----  ---");
    printf("\n");
    for(i=0; i<60; i++) {
      for(j = 0; j<nc-1; j++) {
	C = TamEarthTide(yr, mo, day, hr+j, i, 0, lon, lat, elevation, 0, 0);
	printf("%02d:%02d %4.0f| ", hr+j, i, C);
	}
      C = TamEarthTide(yr, mo, day, hr+j+1, i, 0, lon, lat, elevation, 0, 0);
      printf("%02d:%02d %4.0f\n", hr+j+1, i, C);
      }
    hr += 8;
    printf("\n");
    }
}
