/*
 * dms2dd - convert degrees, minutes, and seconds to dec. degrees
 *
 * compile with:
 *   cc -o dms2dd dms2dd.c
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
  double d, m, s, dd;
  unsigned char sign;

  d = 1;
  while(d != -999.0) {
    sign = 0;
    scanf("%lf %lf %lf", &d, &m, &s);
    if(d == -999.0) continue;
    if(d < 0) {
      sign = 1;
      d *= -1.0;
      }
    dd = d + ( m + (s/60.0) )/60.0;
    if(sign) {
      dd *= -1.0;
      }
    printf("\t%.8lf\n", dd);
    }
}

