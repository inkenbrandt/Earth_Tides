/*
 * dd2dms - convert degrees, minutes, and seconds to dec. degrees
 *
 * compile with:
 *   cc -o dd2dms dd2dms.c
 *
 * USAGE:
 *   run the program
 *   enter degrees, minutes, and seconds as floats, separated
 *     by whitespace.
 *   end by entering a degree value of -999
 *
 * Paul Gettings, University of Utah, May 2001
 */
#include <stdio.h>

int main(void)
{
  int d, m;
  double s, dd;
  unsigned char sign;

  dd = 0;
  while(dd != -999.0) {
    sign = 0;
    scanf("%lf", &dd);
    if(dd == -999.0) continue;
    if(dd < 0) {
      sign = 1;
      dd *= -1.0;
      }
    d = (int)dd;
    m = (int)((dd-d)*60);
    s = (dd-d-m/60.0)*3600;
    if(sign) {
      dd *= -1.0;
      d *= -1.0;
      }
    printf("\t%d %d %lf\n", d, m, s);
    }
}

