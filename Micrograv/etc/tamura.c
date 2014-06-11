#include <math.h>
#include "tamura.h"

#define PI 3.141592653589793
#define RAD 0.0174532925199433
#define FL 3.35281E-3
#define GM 4.902794E12
#define GS 1.327124E20
#define EE 6378137.0
#define KSL 16
#define KSD 7
#define KML 61
#define KMB 45
#define KMD 43
#define INI 1000

double TamEarthTide(int yr, int mh, int dy, int hr, int min, int sec,
	      double lon, double lat, double hi, double tl, double ot)
{
  double gup; // return value, in uGal
  double lonD, gn, ps, cps, sps, rr, zm, zs, time, ut, xt, xx;
  double ea, eb, ss, ds, sss, as, es, sm, dc, dm, cdc, tmp, sdc, am;
  double em, hh, hm, hs, sem, ses, ccm, ccs, bm, bs;
  double gmx, gmy, gmz, gsx, fup, fnt;

  double utst;

// Geocentric lat and radius
  lonD = lon*RAD;
  gn = (FL+0.5*FL*FL)*sin(2.0*lat*RAD) - 0.5*FL*FL *sin(4.0*lat*RAD);
  ps = lat*RAD-gn;
  cps = cos(ps);
  sps = sin(ps);
  rr = EE*(1.0 - FL*sps*sps*(1 + 1.5*FL*cps*cps))+hi;

// Units of uGal
  zm = rr*GM*1.0E8;
  zs = rr*GS*1.0E8;

//
// Origin time
//
  utst = utstart(hr, min, sec, ot);
  time = etstart(yr, mh, dy, utst, tl);
  ut = utst*PI/12.0;
  xt = 0.1/(24*36525.0);
  xx = 0.1*PI/12.0;
//
// Compute away
//
  epsiln(&ea, &eb, time,xt);
// SUN'S POSITION
  ss = sunlon(time);
  ds = sundis(time);
  sss = sin(ss);
  as = atan2(ea*sss,cos(ss));
  es = asin(eb*sss);
// MOON'S POSITION 
  sm = fmoonl(time);
  dc = fmoonb(time);
  dm = fmoond(time);
  cdc = cos(dc);
  tmp = sin(sm)*cdc;
  sdc = sin(dc);
  am = atan2(ea*tmp-eb*sdc,cdc*cos(sm));
  em = asin(ea*sdc+eb*tmp);
// HOUR ANGLES
  hh = gast(ut,time,tl)+lonD;
  hm = hh-am;
  hs = hh-as;
  sem = sin(em);
  ses = sin(es);
  ccm = cos(hm)*cos(em);
  ccs = cos(hs)*cos(es);
  bm = sps*sin(em) + cps*ccm;
  bs = sps*ses + cps*ccs;

// Potential
  gmx = zm/(dm*dm*dm);
  gmy = gmx*rr/dm;
  gmz = gmy*rr/dm;
  gsx = zs/(ds*ds*ds);

// F  UP, NORTH
  fup = gmx*(3*bm*bm - 1) + 
        gmy*(7.5*bm*bm*bm - 4.5*bm) +
        gsx*(3*bs*bs - 1) +
        gmz*(17.5*bm*bm*bm*bm - 15*bm*bm + 1.5);
  fnt = (3*gmx*bm + gmy*(7.5*bm*bm-1.5)) * (cps*sem - sps*ccm) +
        3*gsx*bs*(cps*ses - sps*ccs);

// UPWARD ATTRACTION
  gup = fup+gn*fnt;

//  multiply by gravimetric factor, 1.16
  gup = gup * 1.16;

  return(gup);
}


//
//     LONGITUDE OF THE SUN IN RADIANS   ( NUTATION IS TAKEN INTO ACCOUNT )
//       GRAVITY IS FREE FROM ABERRATION  (-0.0057 DEG.)
//
//       TIME : (JUD-2451545.0)/36525     EPOCH = J2000.0
double sunlon(double time)
{
  double B0=36000.7695, C0=280.4659;
  double A[]={19147.0E-4, 200.0E-4, 48.0E-4, 20.0E-4, 18.0E-4, 18.0E-4,
             15.0E-4,     13.0E-4,  7.0E-4,  7.0E-4,  7.0E-4,  6.0E-4,
              5.0E-4,      5.0E-4,  4.0E-4,  4.0E-4};
  double B[]={35999.05E0, 71998.1E0,  1934.0E0, 32964.0E0,    19.0E0,
            445267.00E0, 45038.0E0, 22519.0E0, 65929.0E0,  3035.0E0,
              9038.00E0, 33718.0E0,   155.0E0,  2281.0E0, 29930.0E0,
             31557.00E0};
  double C[]={267.52E0, 265.1E0, 145.0E0, 158.0E0, 159.0E0, 208.0E0,
             254.00E0, 352.0E0,  45.0E0, 110.0E0,  64.0E0, 316.0E0,
             118.00E0, 221.0E0,  48.0E0, 161.0E0};
  double amp[16], con[16], dif[16];
  double sunlon=0, temp, delta;
  int i;

  A[0] = 1.9147 - 0.0048*time;

  for(i=0; i<16; i++) {
    temp = (B[i]*time+C[i])*RAD;
    sunlon += A[i]*cos(temp);
    }

  sunlon = (sunlon+B0*time+C0)*RAD;
  return(sunlon);
  }


//
//     GEOCENTRIC DISTANCE OF THE SUN IN METERS
//
//       TIME : (JUD-2451545.0)/36525     EPOCH = J2000.0
double sundis(double time)
{
  double A0=1.000140, CS=1.49597870E11;
  double A[]={16706.0E-6, 139.0E-6, 31.0E-6, 16.0E-6, 16.0E-6, 5.0E-6, 5.0E-6};
  double B[]={35999.05E0, 71998.0E0, 445267.0E0, 32964.0E0, 45038.0E0,
	     22519.00E0, 33718.0E0};
  double C[]={177.53E0, 175.0E0, 298.0E0,  68.0E0, 164.0E0, 233.0E0, 226.0E0};
  double au=0, temp;
  int i;

  A[0] = 0.016706 - 0.000042*time;

  for(i=0; i<7; i++) {
    temp = (B[i]*time+C[i])*RAD;
    au += A[i]*cos(temp);
    }
  return((A0+au)*CS);
  }




//
//     APPARENT LONGITUDE OF THE MOON IN RADIANS
//
//       TIME : (JUD-2451545.0)/36525          EPOCH = J2000.0
//       XT   : TIME INTERVAL                  UNIT IN 36525 DAYS
double fmoonl(double time)
{
  double B0=481267.8809, C0=218.3162;
  double A[]={62888.0E-4, 12740.0E-4, 6583.0E-4, 2136.0E-4, 1851.0E-4,
              1144.0E-4,   588.0E-4,  571.0E-4,  533.0E-4,  458.0E-4, 409.0E-4,
               347.0E-4,   304.0E-4,  154.0E-4,  125.0E-4,  110.0E-4, 107.0E-4,
               100.0E-4,    85.0E-4,   79.0E-4,   68.0E-4,   52.0E-4,  50.0E-4, 40.0E-4,
                40.0E-4,    40.0E-4,   38.0E-4,   37.0E-4,   28.0E-4,  27.0E-4, 26.0E-4,
                24.0E-4,    23.0E-4,   22.0E-4,   21.0E-4,   21.0E-4,  21.0E-4, 18.0E-4,
                16.0E-4,    12.0E-4,   11.0E-4,    9.0E-4,    8.0E-4,   7.0E-4,  7.0E-4,
                 7.0E-4,     7.0E-4,    6.0E-4,    6.0E-4,    5.0E-4,   5.0E-4,  5.0E-4,
                 4.0E-4,     4.0E-4,    3.0E-4,    3.0E-4,    3.0E-4,   3.0E-4,  3.0E-4,
                 3.0E-4,     3.0E-4};
  double B[]={477198.868E0,  413335.35E0, 890534.22E0, 954397.74E0,
              35999.050E0,  966404.00E0,  63863.50E0, 377336.30E0,
            1367733.100E0,  854535.20E0, 441199.80E0, 445267.10E0,
             513197.9E0,     75870.0E0, 1443603.0E0,  489205.0E0,1303870.0E0,
            1431597.0E0,    826671.0E0,  449334.0E0,  926533.0E0,  31932.0E0,
             481266.0E0,   1331734.0E0, 1844932.0E0,     133.0E0,1781068.0E0,
             541062.0E0,      1934.0E0,  918399.0E0, 1379739.0E0,  99863.0E0,
             922466.0E0,    818536.0E0,  990397.0E0,   71998.0E0, 341337.0E0,
             401329.0E0,   1856938.0E0, 1267871.0E0, 1920802.0E0, 858602.0E0,
            1403732.0E0,    790672.0E0,  405201.0E0,  485333.0E0,  27864.0E0,
             111869.0E0,   2258267.0E0, 1908795.0E0, 1745069.0E0, 509131.0E0,
              39871.0E0,     12006.0E0,  958465.0E0,  381404.0E0, 349472.0E0,
            1808933.0E0,    549197.0E0,    4067.0E0, 2322131.0E0};
  double C[]={ 44.963E0, 10.74E0, 145.70E0, 179.93E0, 87.53E0,  276.5E0,
             124.2E0,   13.2E0,  280.7E0,  148.2E0,  47.4E0,    27.9E0, 222.5E0,
              41.0E0,   52.0E0,  142.0E0,  246.0E0, 315.0E0,   111.0E0, 188.0E0,
             323.0E0,  107.0E0,  205.0E0,  283.0E0,  56.0E0,    29.0E0,  21.0E0,
             259.0E0,  145.0E0,  182.0E0,   17.0E0, 122.0E0,   163.0E0, 151.0E0,
             357.0E0,   85.0E0,   16.0E0,  274.0E0, 152.0E0,   249.0E0, 186.0E0,
             129.0E0,   98.0E0,  114.0E0,   50.0E0, 186.0E0,   127.0E0,  38.0E0,
             156.0E0,   90.0E0,   24.0E0,  242.0E0, 223.0E0,   187.0E0, 340.0E0,
             354.0E0,  337.0E0,   58.0E0,  220.0E0,  70.0E0,   191.0E0};
  double fmoonl=0, temp;
  int i;

  for(i=0; i<61; i++) {
    temp = (B[i]*time+C[i])*RAD;
    fmoonl += A[i]*cos(temp);
    }
  fmoonl = (fmoonl+B0*time+C0)*RAD;
  return(fmoonl);
}




//
//     APPARENT LATITUDE OF THE MOON IN RADIANS
//
//       TIME : (JUD-2451545.0)/36525      EPOCH = J2000.0
double fmoonb(double time)
{
  double A[]={51281.0E-4, 2806.0E-4, 2777.0E-4, 1733.0E-4, 554.0E-4, 463.0E-4,
	       326.0E-4,  172.0E-4,   93.0E-4,   88.0E-4,   82.0E-4, 43.0E-4, 42.0E-4,
	        34.0E-4,   25.0E-4,   22.0E-4,   22.0E-4,   21.0E-4, 19.0E-4, 18.0E-4,
	        18.0E-4,   18.0E-4,   15.0E-4,   15.0E-4,   15.0E-4, 14.0E-4, 13.0E-4,
	        13.0E-4,   11.0E-4,   10.0E-4,    9.0E-4,    8.0E-4,  7.0E-4,  6.0E-4,
	         6.0E-4,    5.0E-4,    5.0E-4,    5.0E-4,    4.0E-4,  4.0E-4,  3.0E-4,
	         3.0E-4,    3.0E-4,    3.0E-4,    3.0E-4};
  double B[]={483202.019E0,  960400.89E0,  6003.15E0, 407332.20E0,
	     896537.4E0,    69866.7E0, 1373736.2E0,  1437599.8E0,
             884531.0E0,   471196.0E0,  371333.0E0,   547066.0E0,1850935.0E0,
             443331.0E0,   860538.0E0,  481268.0E0,  1337737.0E0, 105866.0E0,
             924402.0E0,   820668.0E0,  519201.0E0,  1449606.0E0,  42002.0E0,
             928469.0E0,   996400.0E0,   29996.0E0,   447203.0E0,  37935.0E0,
            1914799.0E0,  1297866.0E0, 1787072.0E0,   972407.0E0,1309873.0E0,
             559072.0E0,  1361730.0E0,  848532.0E0,   419339.0E0, 948395.0E0,
            2328134.0E0,  1024264.0E0,  932536.0E0,  1409735.0E0,2264270.0E0,
            1814936.0E0,   335334.0E0};
  double C[]={3.273E0, 138.24E0, 48.31E0, 52.43E0, 104.0E0,  82.5E0,
           239.0E0,   273.2E0, 187.0E0,  87.0E0,   55.0E0, 217.0E0,  14.0E0,
           230.0E0,   106.0E0, 308.0E0, 241.0E0,   80.0E0, 141.0E0, 153.0E0,
           181.0E0,    10.0E0,  46.0E0, 121.0E0,  316.0E0, 129.0E0,   6.0E0,
	    65.0E0,    48.0E0, 288.0E0, 340.0E0,  235.0E0, 205.0E0, 134.0E0,
           322.0E0,   190.0E0, 149.0E0, 222.0E0,  149.0E0, 352.0E0, 282.0E0,
	    57.0E0,   115.0E0,  16.0E0,  57.0E0};
  double fmoonb=0;
  int i;

  for(i=0; i<45; i++) {
    fmoonb += A[i]*cos((B[i]*time+C[i])*RAD);
    }
  fmoonb *= RAD;
  return(fmoonb);
}




//
//     GEOCENTRIC DISTANCE OF THE MOON IN METERS
//
//       TIME : (JUD-2451545.0)/36525      EPOCH = J2000.0
double fmoond(double time)
{
  double A0=0.950725;
  double A[]={51820.0E-6, 9530.0E-6, 7842.0E-6, 2824.0E-6, 858.0E-6, 531.0E-6,
         400.0E-6, 319.0E-6, 271.0E-6, 263.0E-6, 197.0E-6, 173.0E-6,
         167.0E-6, 111.0E-6, 103.0E-6,  84.0E-6,  83.0E-6,  78.0E-6,
         73.0E-6, 64.0E-6, 63.0E-6, 41.0E-6, 34.0E-6, 33.0E-6, 31.0E-6,
         30.0E-6, 29.0E-6, 26.0E-6, 23.0E-6, 19.0E-6, 13.0E-6, 13.0E-6,
         13.0E-6, 12.0E-6, 11.0E-6, 11.0E-6, 10.0E-6,  9.0E-6,  7.0E-6,
          7.0E-6,  6.0E-6,  6.0E-6,  5.0E-6};
  double B[]={477198.868E0, 413335.35E0, 890534.22E0, 954397.74E0,
        1367733.1E0,   854535.2E0,  377336.3E0,  441199.8E0,
         445267.0E0, 513198.0E0, 489205.0E0,1431597.0E0,1303870.0E0,
          35999.0E0, 826671.0E0,  63864.0E0, 926533.0E0,1844932.0E0,
        1781068.0E0,1331734.0E0, 449334.0E0, 481266.0E0, 918399.0E0,
         541062.0E0, 922466.0E0,  75870.0E0, 990397.0E0, 818536.0E0,
         553069.0E0,1267871.0E0,1403732.0E0, 341337.0E0, 401329.0E0,
        2258267.0E0,1908795.0E0, 858602.0E0,1745069.0E0, 790672.0E0,
        2322131.0E0,1808933.0E0, 485333.0E0,  99863.0E0, 405201.0E0};
  double C[]={134.963E0, 100.74E0, 235.70E0, 269.93E0, 10.7E0, 238.2E0,
         103.2E0, 137.4E0, 118.0E0, 312.0E0, 232.0E0, 45.0E0, 336.0E0,
         178.0E0, 201.0E0, 214.0E0,  53.0E0, 146.0E0, 111.0E0,  13.0E0,
         278.0E0, 295.0E0, 272.0E0, 349.0E0, 253.0E0, 131.0E0,  87.0E0,
         241.0E0, 266.0E0, 339.0E0, 188.0E0, 106.0E0,   4.0E0, 246.0E0,
         180.0E0, 219.0E0, 114.0E0, 204.0E0, 281.0E0, 148.0E0, 276.0E0,
         212.0E0, 140.0E0};
  double paralx=0;
  int i;

  for(i=0; i<43; i++) {
    paralx += A[i]*cos( (B[i]*time+C[i])*RAD );
    }

  paralx = (paralx+A0)*RAD;
  return(EE/(paralx*(1 - paralx*paralx/6)));
}

//
//     START TIME  (UT  IN HOURS)
//
//       hr  : HOUR
//       min  : MINUTE
//       sec  : SECOND
//       ot : TIME SYSTEM  (JST:OFT=9.D0 , UT:OFT=0.D0)
double utstart(int hr, int min, int sec, double ot)
{
  return ((double)(hr) + (double)(min)/60 + (double)(sec)/3600 - ot);
}

//
//     START TIME  (ET)        EPOCH = J2000.0     (JUD-2451545.0)/36525
//
//       yr   : ORIGIN DATE  YEAR    ( 1901 =< yr =< 2099 )
//       mh   :     "        MONTH
//       dy   :     "        DAY
//       ut   : H,M,S  IN HOURS (UTC)
//       tl   : ET-UT  IN SECONDS
double etstart(int yr, int mh, int dy, double ut, double tl)
{
      int M[]={0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334};
      float day;

// XXX DEBUG
      day  = (float)(yr*365 + M[mh-1] + dy + yr/4 - 730500)
             -0.5 + ut/24 + tl/86400;

      if((yr % 4) == 0 && mh <= 2) {
        day--; // leap years
        }
      return(day/36525.0);
}




//
//     GREENWICH APPARENT SIDEREAL TIME      ( IN RADIANS )
//
//       UT   : UNIVERSAL TIME                         UNIT 1 DAY=2*PI
//       TIME : EPHEMERIS TIME       EPOCH = J2000.0   UNIT 36525 DAYS
//       tl   : ET-UT                                  UNIT SECONDS
double gast(double ut, double time, double tl)
{
  double am, p, gast;

  am = 18.69735 + 2400.05130*(time-tl/3.15576E9);
  p = 0.00029*cos( (1934*time + 145)*RAD );
  gast = PI + ut + (am+p)*PI/12.0;
  return (gast);
}


//
//     OBLIQUITY OF THE ECLIPTIC    (IN RADIANS)
//
//     INPUT DATA    TIME : (JUD-2451545.0)/36525   EPOCH = J2000.0
//                   XT   : TIME INTERVAL           UNIT IN 36525 DAYS
//     OUTPUT DATA   EA   : COS( EPSILON )
//                   EB   : SIN( EPSILON )
int epsiln(double *ea,double *eb, double time, double xt)
{
  double om, dom, deb, temp;

  om = (23.43928 - 0.013014*time + 0.00256*cos( (1934*time+235)*RAD ))*RAD;
  *ea = cos(om);
  *eb = sin(om);
  dom = -( 0.013014 + 0.00256*1934*RAD*sin( (1934*time+235)*RAD ))*RAD*xt;
  deb = sin(dom);
  temp = *ea-*eb*deb;
  *eb = *eb+*ea*deb;
  *ea = temp;
  return(0);
}
