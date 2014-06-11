#include <stdio.h>
#include <f2c.h>
#include "tamura.h"

extern int tatide_(double *C, integer *a, integer *b, integer *c, integer *d,
integer *e, integer *f, double *n, double *p, double *h, double *t, double *o);

int main()
{
  long a, b, c, d, e, f;
  double n, p, h, t, o;
  double C;

  // 25 Dec 1999, 01:01:01 AM, EGI at U of Utah, 1300 m ASL
  // GMT offset is -7 hrs
  a=1999; b=12; c=25; d=1; e=1; f=1; n=-111.827; p=40.759;
  h=1300;t=0;o=-7.0;
  tatide_(&C, &a, &b, &c, &d, &e, &f, &n, &p, &h, &t, &o);
  printf("tatide: %lf\n\n", C);
  C = TamEarthTide(a, b, c, d, e, f, n, p, h, t, o);
  printf("TamEarthTide: %lf\n\n", C);
}

