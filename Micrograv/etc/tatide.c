/* tatide.f -- translated by f2c (version 20000121).
   You must link the resulting object file with the libraries:
	-lf2c -lm   (in that order)
*/

#include "f2c.h"

/* Subroutine */ int tatide_(gup, ja, jb, jc, jd, je, jf, rm, ph, hi, tl, ot)
doublereal *gup;
integer *ja, *jb, *jc, *jd, *je, *jf;
doublereal *rm, *ph, *hi, *tl, *ot;
{
    /* Initialized data */

    static doublereal pi = 3.141592653589793;
    static integer kmb = 45;
    static integer kmd = 43;
    static integer ini = 1000;
    static doublereal rad = .0174532925199433;
    static doublereal fl = .00335281;
    static doublereal gm = 4.902794e12;
    static doublereal gs = 1.327124e20;
    static doublereal ee = 6378137.;
    static integer ksl = 16;
    static integer ksd = 7;
    static integer kml = 61;

    /* System generated locals */
    doublereal d__1, d__2, d__3, d__4, d__5;

    /* Builtin functions */
    double sin(), cos(), atan2(), asin();

    /* Local variables */
    static doublereal time;
    extern doublereal gast_();
    static doublereal utst;
    static integer i__;
    static doublereal ea, eb, dc, dm, gn, as, ds, es, am, em, hh, sm, hm, ps, 
	    rr, ss, zm, hs, ut, xt, zs, bm, bs, xx;
    extern doublereal fmoonb_(), fmoond_();
    extern /* Subroutine */ int epsiln_();
    extern doublereal fmoonl_(), etstar_(), sundis_(), sunlon_(), utstar_();
    static doublereal cdc, ccm, ccs, sdc, dmm, rmd, sem, cps, fnt, ses, ets, 
	    gmx, gmy, gmz, tmp, gsx, fup, sps, sss, uts;


/*  this tide routine taken from */
/*    tideg.f, the TAMURA Gravitational Tide computation program. */
/*   modified to eliminate the recurssive looping for table generation, */
/*      renamed tatide from origional tideg (to save confusion at TFO) */
/*    gravimetric factor of 1.16 is added directly to this routine. */
/*    (in TAMURA program, 1.16 factor was multiplied external to routine.) */

/*      Jan '93, GSP. */


/*     THEORETICAL GRAVITY TIDE CALCULATION FOR SOLID EARTH */

/*     OUTPUT DATA */
/*       GUP     : UPWARD COMPONENT OF GRAVITY TIDE (UNIT IN MICRO GALS) */
/*     INPUT DATA */
/*       JA      : ORIGIN TIME  YEAR (1901 =< JA =< 2099) */
/*       JB      :     "        MONTH */
/*       JC      :     "        DAY */
/*       JD      :     "        HOUR */
/*       JE      :     "        MINUTE */
/*       JF      :     "        SECOND */
/*       RM      : STATION PLACE  EAST LONGITUDE IN DEGREES */
/*       PH      :     "          NORTH LATITUDE     " */
/*       HI      :     "          HEIGHT         IN METERS */
/*       TL      : ET-UT  IN SECONDS */
/*       OT      : TIME SYSTEM   (JST:OT=9.D0,  UT:OT=0.D0) */



/*     ROUGH CHECK OF PARAMETERS */

/*      IF(JA.LE.1900 .OR. JA.GE.2100)  STOP' ERROR IN TIDEG   CHECK JA' */
/*      IF(JB.LE.0 .OR. JB.GE.13)       STOP' ERROR IN TIDEG   CHECK JB' */
/*      IF(JC.LE.0 .OR. JC.GE.32)       STOP' ERROR IN TIDEG   CHECK JC' */
/*      IF(JD.LT.0 .OR. JD.GE.24)       STOP' ERROR IN TIDEG   CHECK JD' */
/*      IF(JE.LT.0 .OR. JE.GE.60)       STOP' ERROR IN TIDEG   CHECK JE' */
/*      IF(JF.LT.0 .OR. JF.GE.60)       STOP' ERROR IN TIDEG   CHECK JF' */
/*      IF(DABS(RM).GT.180.D0)          STOP' ERROR IN TIDEG   CHECK RM' */
/*      IF(DABS(PH).GT. 90.D0)          STOP' ERROR IN TIDEG   CHECK PH' */
/*      IF(DABS(HI).GT.9999.D0)         STOP' ERROR IN TIDEG   CHECK HI' */
/*      IF(TL.LT.0.D0 .OR. TL.GT.99.D0) STOP' ERROR IN TIDEG   CHECK TL' */
/*      IF(DABS(OT).GT.12.D0)           STOP' ERROR IN TIDEG   CHECK OT' */

/*     GEOCENTRIC LATITUDE AND RADIUS */

    rmd = *rm * rad;
/* Computing 2nd power */
    d__1 = fl;
/* Computing 2nd power */
    d__2 = fl;
    gn = (fl + d__1 * d__1 * .5) * sin(*ph * 2. * rad) - d__2 * d__2 * .5 * 
	    sin(*ph * 4. * rad);
    ps = *ph * rad - gn;
    cps = cos(ps);
    sps = sin(ps);
/* Computing 2nd power */
    d__1 = sps;
/* Computing 2nd power */
    d__2 = cps;
    rr = ee * (1. - fl * (d__1 * d__1) * (fl * 1.5 * (d__2 * d__2) + 1.)) + *
	    hi;
/*                                              UNIT IN MICRO GALS */
    zm = rr * gm * 1e8;
    zs = rr * gs * 1e8;

/*     ORIGIN TIME , no-STEP, as this is no longer a table generator!! */

    utst = utstar_(jd, je, jf, ot);
    ets = etstar_(ja, jb, jc, &utst, tl);
    uts = utst * pi / 12.;
    xt = 1.1407711613050423e-7;
    xx = pi * .1 / 12.;

/*     MAIN non-LOOP */

    i__ = 1;
    dmm = 0.;
    time = ets + xt * dmm;
    ut = uts + xx * dmm;
/*                                          COS(EPSILON), SIN(EPSILON) */
    epsiln_(&ea, &eb, &time, &xt, &i__, &ini);
/*                                          SUN'S POSITION */
    ss = sunlon_(&time, &xt, &ksl, &i__, &ini);
    ds = sundis_(&time, &xt, &ksd, &i__, &ini);
    sss = sin(ss);
    as = atan2(ea * sss, cos(ss));
    es = asin(eb * sss);
/*                                          MOON'S POSITION */
    sm = fmoonl_(&time, &xt, &kml, &i__, &ini);
    dc = fmoonb_(&time, &xt, &kmb, &i__, &ini);
    dm = fmoond_(&time, &xt, &kmd, &i__, &ini);
    cdc = cos(dc);
    tmp = sin(sm) * cdc;
    sdc = sin(dc);
    am = atan2(ea * tmp - eb * sdc, cdc * cos(sm));
    em = asin(ea * sdc + eb * tmp);
/*                                          HOUR ANGLES */
    hh = gast_(&ut, &time, tl) + rmd;
    hm = hh - am;
    hs = hh - as;

/*          print*,'cos obliquity of ecliptic = ',EA */
/*          print*,'sin obliquity of ecliptic = ',EB */
/*          print*,'ephemeris time                       ',TIME */
/*          print*,'longitude of the sun in radians =    ',SS */
/*          print*,'distance of the sun in meters = ',DS */
/*          print*,'apparent longitude moon in radians = ',SM */
/*          print*,'apparent latitude moon in radians = ',DC */
/*          print*,'geocentric distance moon in radians = ',DM */
/*          print*,'AS = ',AS,'   ES = ',ES */
/*          print*,'AM = ',AM,'   EM = ',EM */
/*          hhh = GAST(UT,TIME,TL) */
/*          print*,'Greenwich siderial time              ',hhh */
/*          print*,'station longitude                    ',RMD */
/*          print*,'GAST + station longitude =           ',HH */
/*          print*,'GAST + station longitude - AM = ',HM */
/*          print*,'GAST + station longitude - AS = ',HS */
/*                                          ZENITH DISTANCES */
    sem = sin(em);
    ses = sin(es);
    ccm = cos(hm) * cos(em);
    ccs = cos(hs) * cos(es);
    bm = sps * sem + cps * ccm;
    bs = sps * ses + cps * ccs;
/*          print*,'BM = ',BM,'   BS = ',BS */
/*                                          POTENTIAL */
/* Computing 3rd power */
    d__1 = dm;
    gmx = zm / (d__1 * (d__1 * d__1));
    gmy = gmx * rr / dm;
    gmz = gmy * rr / dm;
/* Computing 3rd power */
    d__1 = ds;
    gsx = zs / (d__1 * (d__1 * d__1));
/*          print*,'GMX = ',GMX,'   GMY = ',GMY */
/*          print*,'GMZ = ',GMZ,'   GSX = ',GSX */
/*                                            F  UP, NORTH */
/* Computing 2nd power */
    d__1 = bm;
/* Computing 3rd power */
    d__2 = bm;
/* Computing 2nd power */
    d__3 = bs;
/* Computing 4th power */
    d__4 = bm, d__4 *= d__4;
/* Computing 2nd power */
    d__5 = bm;
    fup = gmx * (d__1 * d__1 * 3. - 1.) + gmy * (d__2 * (d__2 * d__2) * 7.5 - 
	    bm * 4.5) + gsx * (d__3 * d__3 * 3. - 1.) + gmz * (d__4 * d__4 * 
	    17.5 - d__5 * d__5 * 15. + 1.5);
/* Computing 2nd power */
    d__1 = bm;
    fnt = (gmx * 3. * bm + gmy * (d__1 * d__1 * 7.5 - 1.5)) * (cps * sem - 
	    sps * ccm) + gsx * 3. * bs * (cps * ses - sps * ccs);
/*                                          UPWARD ATTRACTION */
    *gup = fup + gn * fnt;
/*          print*,'FUP = ',FUP,'   FNT = ',FNT */
/* L10: */

/*  multiply by gravimetric factor, 1.16 */
    *gup *= 1.16;

    return 0;
} /* tatide_ */

doublereal sunlon_(time, xt, ien, mm, ini)
doublereal *time, *xt;
integer *ien, *mm, *ini;
{
    /* Initialized data */

    static doublereal b0 = 36000.7695;
    static doublereal c0 = 280.4659;
    static doublereal a[16] = { 1.9147,.02,.0048,.002,.0018,.0018,.0015,.0013,
	    7e-4,7e-4,7e-4,6e-4,5e-4,5e-4,4e-4,4e-4 };
    static doublereal b[16] = { 35999.05,71998.1,1934.,32964.,19.,445267.,
	    45038.,22519.,65929.,3035.,9038.,33718.,155.,2281.,29930.,31557. }
	    ;
    static doublereal c__[16] = { 267.52,265.1,145.,158.,159.,208.,254.,352.,
	    45.,110.,64.,316.,118.,221.,48.,161. };
    static doublereal rad = .0174532925199433;

    /* System generated locals */
    integer i__1;
    doublereal ret_val;

    /* Builtin functions */
    double cos(), sin();

    /* Local variables */
    static doublereal temp;
    static integer i__;
    static doublereal delta, tempb, tempc, dif[16], amp[16], con[16];


/*     LONGITUDE OF THE SUN IN RADIANS   ( NUTATION IS TAKEN INTO ACCOUNT ) */
/*       GRAVITY IS FREE FROM ABERRATION  (-0.0057 DEG.) */

/*       TIME : (JED-2451545.0)/36525     EPOCH = J2000.0 */
/*       XT   : TIME INTERVAL             UNIT IN 36525 DAYS */
/*       IEN  : PRECISION                 ( TERMS =< 16 ) */
/*       MM   : COUNTER */
/*       INI  : INTERVAL OF INITIALIZATION */




    ret_val = 0.;

    if ((*mm - 1) % *ini == 0) {

/*       INITIALIZE */

	a[0] = 1.9147 - *time * .0048;
	delta = *xt * .5 * rad;

	i__1 = *ien;
	for (i__ = 1; i__ <= i__1; ++i__) {
	    tempb = (b[i__ - 1] * *time + c__[i__ - 1]) * rad;
	    tempc = b[i__ - 1] * delta;
	    amp[i__ - 1] = a[i__ - 1] * cos(tempb);
	    ret_val += amp[i__ - 1];
	    temp = sin(tempc) * 2.;
	    con[i__ - 1] = temp * temp;
	    dif[i__ - 1] = a[i__ - 1] * temp * sin(tempc - tempb);
/* L20: */
	}

    } else {

/*       RECURRENCE FORMULA */

	i__1 = *ien;
	for (i__ = 1; i__ <= i__1; ++i__) {
	    dif[i__ - 1] -= amp[i__ - 1] * con[i__ - 1];
	    amp[i__ - 1] += dif[i__ - 1];
	    ret_val += amp[i__ - 1];
/* L120: */
	}

    }

    ret_val = (ret_val + b0 * *time + c0) * rad;
/*     SUNLON = SUNLON-0.0057D0*RAD       /+ CORRECTION OF ABERATION +/ */

    return ret_val;
} /* sunlon_ */

doublereal sundis_(time, xt, ien, mm, ini)
doublereal *time, *xt;
integer *ien, *mm, *ini;
{
    /* Initialized data */

    static doublereal a0 = 1.00014;
    static doublereal cs = 1.4959787e11;
    static doublereal a[7] = { .016706,1.39e-4,3.1e-5,1.6e-5,1.6e-5,5e-6,5e-6 
	    };
    static doublereal b[7] = { 35999.05,71998.,445267.,32964.,45038.,22519.,
	    33718. };
    static doublereal c__[7] = { 177.53,175.,298.,68.,164.,233.,226. };
    static doublereal rad = .0174532925199433;

    /* System generated locals */
    integer i__1;
    doublereal ret_val;

    /* Builtin functions */
    double cos(), sin();

    /* Local variables */
    static doublereal temp;
    static integer i__;
    static doublereal delta, tempb, tempc, au, dif[7], amp[7], con[7];


/*     GEOCENTRIC DISTANCE OF THE SUN IN METERS */

/*       TIME : (JED-2451545.0)/36525     EPOCH = J2000.0 */
/*       XT   : TIME INTERVAL             UNITS IN 36525 DAYS */
/*       IEN  : PRECISION                 ( TERMS =< 7 ) */
/*       MM   : COUNTER */
/*       INI  : INTERVAL OF INITIALIZATION */




    au = 0.;

    if ((*mm - 1) % *ini == 0) {

/*       INITIALIZE */

	delta = *xt * .5 * rad;
	a[0] = .016706 - *time * 4.2e-5;

	i__1 = *ien;
	for (i__ = 1; i__ <= i__1; ++i__) {
	    tempb = (b[i__ - 1] * *time + c__[i__ - 1]) * rad;
	    tempc = b[i__ - 1] * delta;
	    amp[i__ - 1] = a[i__ - 1] * cos(tempb);
	    au += amp[i__ - 1];
	    temp = sin(tempc) * 2.;
	    con[i__ - 1] = temp * temp;
	    dif[i__ - 1] = a[i__ - 1] * temp * sin(tempc - tempb);
/* L20: */
	}

    } else {

/*       RECURRENCE FORMULA */

	i__1 = *ien;
	for (i__ = 1; i__ <= i__1; ++i__) {
	    dif[i__ - 1] -= amp[i__ - 1] * con[i__ - 1];
	    amp[i__ - 1] += dif[i__ - 1];
	    au += amp[i__ - 1];
/* L120: */
	}

    }

    ret_val = (a0 + au) * cs;

    return ret_val;
} /* sundis_ */

doublereal fmoonl_(time, xt, ien, mm, ini)
doublereal *time, *xt;
integer *ien, *mm, *ini;
{
    /* Initialized data */

    static doublereal b0 = 481267.8809;
    static doublereal c0 = 218.3162;
    static doublereal a[61] = { 6.2888,1.274,.6583,.2136,.1851,.1144,.0588,
	    .0571,.0533,.0458,.0409,.0347,.0304,.0154,.0125,.011,.0107,.01,
	    .0085,.0079,.0068,.0052,.005,.004,.004,.004,.0038,.0037,.0028,
	    .0027,.0026,.0024,.0023,.0022,.0021,.0021,.0021,.0018,.0016,.0012,
	    .0011,9e-4,8e-4,7e-4,7e-4,7e-4,7e-4,6e-4,6e-4,5e-4,5e-4,5e-4,4e-4,
	    4e-4,3e-4,3e-4,3e-4,3e-4,3e-4,3e-4,3e-4 };
    static doublereal b[61] = { 477198.868,413335.35,890534.22,954397.74,
	    35999.05,966404.,63863.5,377336.3,1367733.1,854535.2,441199.8,
	    445267.1,513197.9,75870.,1443603.,489205.,1303870.,1431597.,
	    826671.,449334.,926533.,31932.,481266.,1331734.,1844932.,133.,
	    1781068.,541062.,1934.,918399.,1379739.,99863.,922466.,818536.,
	    990397.,71998.,341337.,401329.,1856938.,1267871.,1920802.,858602.,
	    1403732.,790672.,405201.,485333.,27864.,111869.,2258267.,1908795.,
	    1745069.,509131.,39871.,12006.,958465.,381404.,349472.,1808933.,
	    549197.,4067.,2322131. };
    static doublereal c__[61] = { 44.963,10.74,145.7,179.93,87.53,276.5,124.2,
	    13.2,280.7,148.2,47.4,27.9,222.5,41.,52.,142.,246.,315.,111.,188.,
	    323.,107.,205.,283.,56.,29.,21.,259.,145.,182.,17.,122.,163.,151.,
	    357.,85.,16.,274.,152.,249.,186.,129.,98.,114.,50.,186.,127.,38.,
	    156.,90.,24.,242.,223.,187.,340.,354.,337.,58.,220.,70.,191. };
    static doublereal rad = .0174532925199433;

    /* System generated locals */
    integer i__1;
    doublereal ret_val;

    /* Builtin functions */
    double cos(), sin();

    /* Local variables */
    static doublereal temp;
    static integer i__;
    static doublereal delta, tempb, tempc, dif[61], amp[61], con[61];


/*     APPARENT LONGITUDE OF THE MOON IN RADIANS */

/*       TIME : (JED-2451545.0)/36525          EPOCH = J2000.0 */
/*       XT   : TIME INTERVAL                  UNIT IN 36525 DAYS */
/*       IEN  : PRECISION                      ( TERMS =< 61 ) */
/*       MM   : COUNTER */
/*       INI  : INTERVAL OF INITIALIZATION */




    ret_val = 0.;

    if ((*mm - 1) % *ini == 0) {

/*       INITIALIZE */

	delta = *xt * .5 * rad;

	i__1 = *ien;
	for (i__ = 1; i__ <= i__1; ++i__) {
	    tempb = (b[i__ - 1] * *time + c__[i__ - 1]) * rad;
	    tempc = b[i__ - 1] * delta;
	    amp[i__ - 1] = a[i__ - 1] * cos(tempb);
	    ret_val += amp[i__ - 1];
	    temp = sin(tempc) * 2.;
	    con[i__ - 1] = temp * temp;
	    dif[i__ - 1] = a[i__ - 1] * temp * sin(tempc - tempb);
/* L20: */
	}

    } else {

/*       RECURRENCE FORMULA */

	i__1 = *ien;
	for (i__ = 1; i__ <= i__1; ++i__) {
	    dif[i__ - 1] -= amp[i__ - 1] * con[i__ - 1];
	    amp[i__ - 1] += dif[i__ - 1];
	    ret_val += amp[i__ - 1];
/* L120: */
	}

    }

    ret_val = (ret_val + b0 * *time + c0) * rad;

    return ret_val;
} /* fmoonl_ */

doublereal fmoonb_(time, xt, ien, mm, ini)
doublereal *time, *xt;
integer *ien, *mm, *ini;
{
    /* Initialized data */

    static doublereal a[45] = { 5.1281,.2806,.2777,.1733,.0554,.0463,.0326,
	    .0172,.0093,.0088,.0082,.0043,.0042,.0034,.0025,.0022,.0022,.0021,
	    .0019,.0018,.0018,.0018,.0015,.0015,.0015,.0014,.0013,.0013,.0011,
	    .001,9e-4,8e-4,7e-4,6e-4,6e-4,5e-4,5e-4,5e-4,4e-4,4e-4,3e-4,3e-4,
	    3e-4,3e-4,3e-4 };
    static doublereal b[45] = { 483202.019,960400.89,6003.15,407332.2,
	    896537.4,69866.7,1373736.2,1437599.8,884531.,471196.,371333.,
	    547066.,1850935.,443331.,860538.,481268.,1337737.,105866.,924402.,
	    820668.,519201.,1449606.,42002.,928469.,996400.,29996.,447203.,
	    37935.,1914799.,1297866.,1787072.,972407.,1309873.,559072.,
	    1361730.,848532.,419339.,948395.,2328134.,1024264.,932536.,
	    1409735.,2264270.,1814936.,335334. };
    static doublereal c__[45] = { 3.273,138.24,48.31,52.43,104.,82.5,239.,
	    273.2,187.,87.,55.,217.,14.,230.,106.,308.,241.,80.,141.,153.,
	    181.,10.,46.,121.,316.,129.,6.,65.,48.,288.,340.,235.,205.,134.,
	    322.,190.,149.,222.,149.,352.,282.,57.,115.,16.,57. };
    static doublereal rad = .0174532925199433;

    /* System generated locals */
    integer i__1;
    doublereal ret_val;

    /* Builtin functions */
    double cos(), sin();

    /* Local variables */
    static doublereal temp;
    static integer i__;
    static doublereal delta, tempb, tempc, dif[45], amp[45], con[45];


/*     APPARENT LATITUDE OF THE MOON IN RADIANS */

/*       TIME : (JED-2451545.0)/36525      EPOCH = J2000.0 */
/*       XT   : TIME INTERVAL              UNIT IN 36525 DAYS */
/*       IEN  : PRECISION                  ( TERMS =< 45 ) */
/*       MM   : COUNTER */
/*       INI  : INTERVAL OF INITIALIZATION */




    ret_val = 0.;

    if ((*mm - 1) % *ini == 0) {

/*       INITIALIZE */

	delta = *xt * .5 * rad;

	i__1 = *ien;
	for (i__ = 1; i__ <= i__1; ++i__) {
	    tempb = (b[i__ - 1] * *time + c__[i__ - 1]) * rad;
	    tempc = b[i__ - 1] * delta;
	    amp[i__ - 1] = a[i__ - 1] * cos(tempb);
	    ret_val += amp[i__ - 1];
	    temp = sin(tempc) * 2.;
	    con[i__ - 1] = temp * temp;
	    dif[i__ - 1] = a[i__ - 1] * temp * sin(tempc - tempb);
/* L20: */
	}

    } else {

/*       RECURRENCE FORMULA */

	i__1 = *ien;
	for (i__ = 1; i__ <= i__1; ++i__) {
	    dif[i__ - 1] -= amp[i__ - 1] * con[i__ - 1];
	    amp[i__ - 1] += dif[i__ - 1];
	    ret_val += amp[i__ - 1];
/* L120: */
	}

    }

    ret_val *= rad;

    return ret_val;
} /* fmoonb_ */

doublereal fmoond_(time, xt, ien, mm, ini)
doublereal *time, *xt;
integer *ien, *mm, *ini;
{
    /* Initialized data */

    static doublereal a0 = .950725;
    static doublereal a[43] = { .05182,.00953,.007842,.002824,8.58e-4,5.31e-4,
	    4e-4,3.19e-4,2.71e-4,2.63e-4,1.97e-4,1.73e-4,1.67e-4,1.11e-4,
	    1.03e-4,8.4e-5,8.3e-5,7.8e-5,7.3e-5,6.4e-5,6.3e-5,4.1e-5,3.4e-5,
	    3.3e-5,3.1e-5,3e-5,2.9e-5,2.6e-5,2.3e-5,1.9e-5,1.3e-5,1.3e-5,
	    1.3e-5,1.2e-5,1.1e-5,1.1e-5,1e-5,9e-6,7e-6,7e-6,6e-6,6e-6,5e-6 };
    static doublereal b[43] = { 477198.868,413335.35,890534.22,954397.74,
	    1367733.1,854535.2,377336.3,441199.8,445267.,513198.,489205.,
	    1431597.,1303870.,35999.,826671.,63864.,926533.,1844932.,1781068.,
	    1331734.,449334.,481266.,918399.,541062.,922466.,75870.,990397.,
	    818536.,553069.,1267871.,1403732.,341337.,401329.,2258267.,
	    1908795.,858602.,1745069.,790672.,2322131.,1808933.,485333.,
	    99863.,405201. };
    static doublereal c__[43] = { 134.963,100.74,235.7,269.93,10.7,238.2,
	    103.2,137.4,118.,312.,232.,45.,336.,178.,201.,214.,53.,146.,111.,
	    13.,278.,295.,272.,349.,253.,131.,87.,241.,266.,339.,188.,106.,4.,
	    246.,180.,219.,114.,204.,281.,148.,276.,212.,140. };
    static doublereal rad = .0174532925199433;
    static doublereal ee = 6378137.;

    /* System generated locals */
    integer i__1;
    doublereal ret_val;

    /* Builtin functions */
    double cos(), sin();

    /* Local variables */
    static doublereal temp;
    static integer i__;
    static doublereal delta, tempb, tempc, paralx, dif[43], amp[43], con[43];


/*     GEOCENTRIC DISTANCE OF THE MOON IN METERS */

/*       TIME : (JED-2451545.0)/36525      EPOCH = J2000.0 */
/*       XT   : TIME INTERVAL              UNIT IN 36525 DAYS */
/*       IEN  : PRECISION                  ( TERMS =< 43 ) */
/*       MM   : COUNTER */
/*       INI  : INTERVAL OF INITIALIZATION */




    paralx = 0.;

    if ((*mm - 1) % *ini == 0) {

/*       INITIALIZE */

	delta = *xt * .5 * rad;

	i__1 = *ien;
	for (i__ = 1; i__ <= i__1; ++i__) {
	    tempb = (b[i__ - 1] * *time + c__[i__ - 1]) * rad;
	    tempc = b[i__ - 1] * delta;
	    amp[i__ - 1] = a[i__ - 1] * cos(tempb);
	    paralx += amp[i__ - 1];
	    temp = sin(tempc) * 2.;
	    con[i__ - 1] = temp * temp;
	    dif[i__ - 1] = a[i__ - 1] * temp * sin(tempc - tempb);
/* L20: */
	}

    } else {

/*       RECURRENCE FORMULA */

	i__1 = *ien;
	for (i__ = 1; i__ <= i__1; ++i__) {
	    dif[i__ - 1] -= amp[i__ - 1] * con[i__ - 1];
	    amp[i__ - 1] += dif[i__ - 1];
	    paralx += amp[i__ - 1];
/* L120: */
	}

    }

    paralx = (paralx + a0) * rad;
    ret_val = ee / (paralx * (1. - paralx * paralx / 6.));

    return ret_val;
} /* fmoond_ */

doublereal utstar_(jd, je, jf, oft)
integer *jd, *je, *jf;
doublereal *oft;
{
    /* System generated locals */
    doublereal ret_val;


/*     START TIME  (UT  IN HOURS) */

/*       JD  : HOUR */
/*       JE  : MINUTE */
/*       JF  : SECOND */
/*       OFT : TIME SYSTEM  (JST:OFT=9.D0 , UT:OFT=0.D0) */


    ret_val = (doublereal) (*jd) + (doublereal) (*je) / 60. + (doublereal) (*
	    jf) / 3600. - *oft;

    return ret_val;
} /* utstar_ */

doublereal etstar_(ja, jb, jc, utst, tl)
integer *ja, *jb, *jc;
doublereal *utst, *tl;
{
    /* Initialized data */

    static integer m[12] = { 0,31,59,90,120,151,181,212,243,273,304,334 };

    /* System generated locals */
    doublereal ret_val;

    /* Local variables */
    static doublereal day;


/*     START TIME  (ET)        EPOCH = J2000.0     (JED-2451545.0)/36525 */

/*       JA   : ORIGIN DATE  YEAR    ( 1901 =< JA =< 2099 ) */
/*       JB   :     "        MONTH */
/*       JC   :     "        DAY */
/*       UTST : H,M,S  IN HOURS */
/*       TL   : ET-UT  IN SECONDS */



    day = (doublereal) (*ja * 365 + m[(0 + (0 + (*jb - 1 << 2))) / 4] + *jc + 
	    *ja / 4 - 730500) - .5 + *utst / 24. + *tl / 86400.;

    if (*ja % 4 == 0 && *jb <= 2) {
	day += -1.;
    }

    ret_val = day / 36525.;

    return ret_val;
} /* etstar_ */

doublereal gast_(ut, time, tl)
doublereal *ut, *time, *tl;
{
    /* Initialized data */

    static doublereal pi = 3.141592653589793;
    static doublereal rad = .0174532925199433;

    /* System generated locals */
    doublereal ret_val;

    /* Builtin functions */
    double cos();

    /* Local variables */
    static doublereal p, am;


/*     GREENWICH APPARENT SIDEREAL TIME      ( IN RADIANS ) */

/*       UT   : UNIVERSAL TIME                         UNIT 1 DAY=2*PI */
/*       TIME : EPHEMERIS TIME       EPOCH = J2000.0   UNIT 36525 DAYS */
/*       TL   : ET-UT                                  UNIT SECONDS */



    am = 18.69735 + 2400.0513 * (*time - *tl / 3.15576e9);
    p = cos((*time * 1934. + 145.) * rad) * 2.9e-4;
    ret_val = pi + *ut + (am + p) * pi / 12.;

    return ret_val;
} /* gast_ */

/* Subroutine */ int epsiln_(ea, eb, time, xt, mm, ini)
doublereal *ea, *eb, *time, *xt;
integer *mm, *ini;
{
    /* Initialized data */

    static doublereal rad = .0174532925199433;

    /* Builtin functions */
    double cos(), sin();

    /* Local variables */
    static doublereal temp, om, deb, dom;


/*     OBLIQUITY OF THE ECLIPTIC    (IN RADIANS) */

/*     INPUT DATA    TIME : (JED-2451545.0)/36525   EPOCH = J2000.0 */
/*                   XT   : TIME INTERVAL           UNIT IN 36525 DAYS */
/*                   MM   : COUNTER */
/*                   INI  : INTERVAL OF INITIALIZATION */
/*     OUTPUT DATA   EA   : COS( EPSILON ) */
/*                   EB   : SIN( EPSILON ) */



    if ((*mm - 1) % *ini == 0) {

/*       INITIALIZE */

	om = (23.43928 - *time * .013014 + cos((*time * 1934. + 235.) * rad) *
		 .00256) * rad;
	*ea = cos(om);
	*eb = sin(om);
	dom = -(rad * 4.9510400000000008 * sin((*time * 1934. + 235.) * rad) 
		+ .013014) * rad * *xt;
	deb = sin(dom);

    } else {

/*       RECURRENCE FORMULA */

	temp = *ea - *eb * deb;
	*eb += *ea * deb;
	*ea = temp;

    }

    return 0;
} /* epsiln_ */

