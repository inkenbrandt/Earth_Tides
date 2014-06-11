/* originally translated from longman.f by f2c
   main routine added by hand

   You must link the resulting object file with the libraries:
	-lf2c -lm   (in that order)
*/


#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "f2c.h"


void julian2date(double jd, int *year, int *day, int *time);

int main(int argc, char *argv[])
{
  double elevation, lat, lon, latsec, lonsec;
  double jd;
  int tgmt, year, day;
  double C;

  if(argc < 5) {
    printf("usage: %s <lat> <lon> <elevation> <julian day>\n", argv[0]);
    printf("where lat/lon are in decimal degrees, positive north/east;\n");
    printf("      elevation in meters;\n");
    printf("      julian day in fractional days, referenced to GMT\n");
    exit(0);
    }
  /* usage: longman lat lon elevation jul_day */
  lat = atof(argv[1]);
  lon = atof(argv[2]);
  elevation = atof(argv[3]);
  jd = atof(argv[4]);

  /* convert numbers for feeding to tideg_ */
  latsec = latsec*3600.0;
  lonsec = -1.0*latsec*3600.0;
  elevation /= 0.3048;

  julian2date(jd, &year, &day, &tgmt);

  tideg_(&latsec, &lonsec, &elevation, &year, &day, &tgmt, &C);

  printf("%lf\n", C);
}
/*      call tideg(seclat, seclon, etid, year, ida, tgmt, tidee) */

int tideg_(latsec, longsc, elev, year, ida, tgmt, tidee)
real *latsec, *longsc, *elev;
integer *year, *ida, *tgmt;
real *tidee;
{
/*  **  ref: jgr,64,#12,p2351,1959. */
/* 	latsec,longsc-latitude&longitude in seconds */
/*  **  longitude measured + to west,- to east, */
/*  **  range 0-180 degrees. */
/* 	elev- elevation in feet */
/* 	year- 4 digit integer year */
/* 	ida- day of year (1-366) */
/* 	tgmt- greenwich standard time (4 digit integer) */
/* 	tidee- earth tide correction,mgals */

    /* Initialized data */

    static doublereal ds[4] = { 4.720023438334786,8399.709299532332,
	    4.406955783270416e-5,3.296732560239086e-8 };
    static doublereal dp[4] = { 5.835124720906877,71.01800935662992,
	    1.805445068160927e-4,2.181661351142696e-7 };
    static doublereal ps[4] = { 4.908229466864464,.03000526416797298,
	    7.902455899166507e-6,5.817762968100108e-8 };
    static doublereal dn[4] = { 4.5235885702679,33.7571530339432,
	    3.674887600803287e-5,3.878507587154933e-8 };
    static doublereal dh[3] = { 4.881627934044856,628.3319509908986,
	    5.279618520477778e-6 };
    static doublereal dcmeg = .91739374;
    static doublereal dsmeg = .39798093;
    static doublereal dcii = .99597102;
    static doublereal dsii = .089676321;

    /* System generated locals */
    doublereal d__1, d__2, d__3, d__4;

    /* Builtin functions */
    double cos(), sqrt(), atan2(), sin(), atan();

    /* Local variables */
    static integer ieer;
    static doublereal tani, cosi, sini, asun, dsun, esun, gsun, xgmt, lsun, 
	    psun, ocos2, osin2, h__;
    static integer i__, j;
    static doublereal n, lamda, p, s, t, alpha, v, omega, sigma, hcosi, hsini,
	     thran, gmoon, costh, gmoon1, gmoon2, bb, cc, dd, ci, ii, calpha, 
	    vc;
    extern /* Subroutine */ int ju_();
    static doublereal salpha, vs, cosphi, radius, chisun, vo2, deg, chi, rad, 
	    rdd, sdd;
    static integer day;
    static doublereal sff, xll, rdd1, rdd2, rdd3, rdd4, xll1, xll2;

    omega = .409315;
    ii = .089797;
    rad = .017453292519943;
    deg = (doublereal) (*longsc) / 3600.;
    lamda = (doublereal) (*latsec) / 3600. * rad;
    day = *ida - 1;
    ju_(year, &day, tgmt, &ieer, &t);
/* compute intermediate variables s,p,h */
    if (ieer != 0) {
	goto L10;
    }
/* Computing 2nd power */
    d__1 = t;
    h__ = dh[0] + dh[1] * t + dh[2] * (d__1 * d__1);
/* Computing 2nd power */
    d__1 = t;
/* Computing 3rd power */
    d__2 = t;
    s = ds[0] + ds[1] * t + ds[2] * (d__1 * d__1) + ds[3] * (d__2 * (d__2 * 
	    d__2));
/* compute sigma---mean longitude od moon reckoned from ascending */
/*      intersection of moon orbit with equator */
/* Computing 2nd power */
    d__1 = t;
/* Computing 3rd power */
    d__2 = t;
    p = dp[0] + dp[1] * t - dp[2] * (d__1 * d__1) - dp[3] * (d__2 * (d__2 * 
	    d__2));
/* Computing 2nd power */
    d__1 = t;
/* Computing 3rd power */
    d__2 = t;
    n = dn[0] - dn[1] * t + dn[2] * (d__1 * d__1) + dn[3] * (d__2 * (d__2 * 
	    d__2));
    cosi = dcmeg * dcii - dsmeg * dsii * cos(n);
/* Computing 2nd power */
    d__1 = cosi;
    sini = sqrt(1. - d__1 * d__1);
    tani = atan2(sini, cosi);
    vs = dsii * sin(n) / sin(tani);
/* Computing 2nd power */
    d__1 = vs;
    vo2 = sqrt(1. - d__1 * d__1);
    v = atan2(vs, vo2);
    vc = vo2;
    calpha = cos(n) * vc + sin(n) * vs * dcmeg;
    salpha = dsmeg * sin(n) / sin(tani);
    alpha = atan(salpha / (calpha + 1.)) * 2.;
/* compute chi----right ascension of meridian of point reckoned */
/*      from ascending moon-equator intersection */
    sigma = s + alpha - n;
    i__ = *tgmt % 100;
    j = (*tgmt - i__) / 100;
    xgmt = (doublereal) j + (doublereal) i__ / 60.;
    thran = ((xgmt - 12.) * 15. - deg) * rad;
/* compute xll----longitude of moon in its orbit from ascending */
/*      intersection with equator */
/*           eccentricity = 0.05490 */
/*      ratio of sun/moon motion = 0.074804 */
    chi = thran + h__ - v;
    xll1 = sigma + sin(s - p) * .1098 + sin((s - p) * 2.) * .003768;
    xll2 = sin(s - h__ * 2. + p) * .0154 + sin((s - h__) * 2.) * .007694;
/* compute costh---zenith angle of moon */
    xll = xll1 + xll2;
    hcosi = sqrt((cosi + 1.) / 2.);
    hsini = sqrt((1. - cosi) / 2.);
/* Computing 2nd power */
    d__1 = hcosi;
/* Computing 2nd power */
    d__2 = hsini;
    bb = d__1 * d__1 * cos(xll - chi) + d__2 * d__2 * cos(xll + chi);
/* compute dd----distance between centers of the moon and earth */
    costh = sin(lamda) * sini * sin(xll) + cos(lamda) * bb;
    rdd1 = cos(s - p) * 1.4325e-12 + 2.60144e-11;
    rdd2 = cos((s - p) * 2.) * 7.86439e-14;
    rdd3 = cos(s - h__ * 2. + p) * 2.0092e-13;
    rdd4 = cos((s - h__) * 2.) * 1.46008e-13;
    rdd = rdd1 + rdd2 + rdd3 + rdd4;
/* compute rr----radius of the earth at p */
    dd = 1. / rdd;
/* Computing 2nd power */
    d__1 = sin(lamda);
    ci = 1. / (d__1 * d__1 * .006738 + 1.);
    radius = sqrt(ci) * 6.37827e8 + (doublereal) (*elev * (float)30.48);
/* Computing 3rd power */
    d__1 = dd;
/* Computing 2nd power */
    d__2 = costh;
    gmoon1 = radius * 4.9049e18 / (d__1 * (d__1 * d__1)) * (d__2 * d__2 * 3. 
	    - 1.);
/* Computing 2nd power */
    d__1 = dd;
/* Computing 2nd power */
    d__2 = radius;
/* Computing 2nd power */
    d__3 = dd;
/* Computing 3rd power */
    d__4 = costh;
    gmoon2 = 7.3574e18 / (d__1 * d__1) * (d__2 * d__2 / (d__3 * d__3)) * (
	    d__4 * (d__4 * d__4) * 5. - costh * 3.);
    gmoon = gmoon1 + gmoon2;
/* Computing 2nd power */
    d__1 = t;
/* Computing 3rd power */
    d__2 = t;
    psun = ps[0] + ps[1] * t + ps[2] * (d__1 * d__1) + ps[3] * (d__2 * (d__2 *
	     d__2));
/* Computing 2nd power */
    d__1 = t;
    esun = .01675104 - t * 4.18e-5 - d__1 * d__1 * 1.26e-7;
    lsun = h__ + esun * 2. * sin(h__ - psun);
    chisun = thran + h__;
    ocos2 = cos(omega / 2.);
    osin2 = sin(omega / 2.);
/* Computing 2nd power */
    d__1 = ocos2;
/* Computing 2nd power */
    d__2 = osin2;
    cc = d__1 * d__1 * cos(lsun - chisun) + d__2 * d__2 * cos(lsun + chisun);
/* compute d---distance between earth and sun */
    cosphi = sin(lamda) * dsmeg * sin(lsun) + cos(lamda) * cc;
/* Computing 2nd power */
    d__1 = esun;
    asun = 1. / ((1. - d__1 * d__1) * 1.495e13);
    sdd = asun * esun * cos(h__ - psun) + 6.68896e-14;
    dsun = 1. / sdd;
/* Computing 2nd power */
    d__1 = cosphi;
    sff = d__1 * d__1 * 3. - 1.;
/* Computing 2nd power */
    d__1 = dsun;
    gsun = 1.329e26 / (d__1 * d__1) * (radius / dsun) * sff;
    *tidee = (real) (gsun + gmoon) / (float).001 * (float)1.2;
L10:
    return 0;
} /* tideg_ */


void julian2date(double jd, int *year, int *day, int *time)
{
  double fract_day;
  int Q1, R1, Q2, R2;

  jd += 0.5;
  jd -= 59;
  fract_day = jd - floor(jd);

  if(fract_day < 0) {
    fract_day += 1.0;
    jd -= 1;
    }

  Q1 = floor(jd)/1461;
  R1 = (int)(floor(jd)) % 1461;
  Q2 = floor(R1/365.0);
  R2 = R1 % 365;
  *year = 4*Q1 + Q2;
  *year -= 4712;
  *day = R2 + 13;
  *time = fract_day*24.0;
}
