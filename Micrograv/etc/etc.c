/* C interface to tamura.c - translation of Tamura's Earth Tide program
tatide.f */
#include "python2.3/Python.h"
#include <math.h>
#include "tamura.h"

/* Python interface functions */
void initetc(void);
static PyObject *etc(PyObject *self, PyObject *args);

static PyMethodDef ETCMethods[]={{"tide", etc, METH_VARARGS}, {NULL, NULL}};

void initetc(void)
{
	(void) Py_InitModule("etc", ETCMethods);
}

static PyObject *etc(PyObject *self, PyObject *args)
{
  int year, month, day, hour, minute, seconds;
  int a,b,c,d,e,f;
  double n,p,h,t,o;
  double lat, lon;
  double hi, gmt_off;
  double C;
  double tl, ot;

  int ok;

  PyObject *rval;
  /* parse Python args into C vars */
  ok = PyArg_ParseTuple(args, "iiiiiiddddd", &year, &month, &day, &hour, &minute, &seconds,
    &lon, &lat, &hi, &tl, &gmt_off);

  /* call tatide */
  a=year;b=month;c=day;d=hour;e=minute;f=seconds;
  n=lon;p=lat;h=hi;
  o=gmt_off;t=tl;

  C = TamEarthTide(a, b, c, d, e, f, n, p, h, t, o);

  rval = Py_BuildValue("d", C);
  return rval;
}
