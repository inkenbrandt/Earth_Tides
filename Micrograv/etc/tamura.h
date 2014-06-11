#ifndef TAMURA_ETC
#define TAMURA_ETC

// TamEarthTide() - Compute Earth Tide Correction for gravity, in uGal!
//
// type name        description
// ---- ----        -----------
// int   yr      :  TIME  YEAR (1901 =< yr =< 2099)
// int   mh      :     "  MONTH
// int   dy      :     "  DAY
// int   hr      :     "  HOUR 
// int   min     :     "  MINUTE
// int   sec     :     "  SECOND
// dbl   lon     : STATION PLACE  EAST LONGITUDE IN DEGREES
// dbl   lat     :     "          NORTH LATITUDE     "
// dbl   hi      :     "          HEIGHT         IN METERS
// dbl   tl      : ET-UT  IN SECONDS
// dbl   ot      : GMT offset, in hours   (JST:ot=9,  UTC:ot=0)
//    NOTE: ET - epoch time; UT - Universal Time (UTC or GMT)
//
// Be sure to link with math library!
//
double TamEarthTide(int yr, int mh, int dy, int hr, int min, int sec,
	      double lon, double lat, double hi, double tl, double ot);

// The remaining routines are internal to TamEarthTide, although they
// may be of use in other settings.

//
//     LONGITUDE OF THE SUN IN RADIANS   ( NUTATION IS TAKEN INTO ACCOUNT )
//       GRAVITY IS FREE FROM ABERRATION  (-0.0057 DEG.)
//
//       TIME : (JUD-2451545.0)/36525     EPOCH = J2000.0
double sunlon(double time);

//
//     GEOCENTRIC DISTANCE OF THE SUN IN METERS
//
//       TIME : (JUD-2451545.0)/36525     EPOCH = J2000.0
double sundis(double time);

//
//     APPARENT LONGITUDE OF THE MOON IN RADIANS
//
//       TIME : (JUD-2451545.0)/36525          EPOCH = J2000.0
//       XT   : TIME INTERVAL                  UNIT IN 36525 DAYS
double fmoonl(double time);

//
//     APPARENT LATITUDE OF THE MOON IN RADIANS
//
//       TIME : (JUD-2451545.0)/36525      EPOCH = J2000.0
double fmoonb(double time);

//
//     GEOCENTRIC DISTANCE OF THE MOON IN METERS
//
//       TIME : (JUD-2451545.0)/36525      EPOCH = J2000.0
double fmoond(double time);

//
//     START TIME  (UT  IN HOURS)
//
//       hr  : HOUR
//       min  : MINUTE
//       sec  : SECOND
//       ot : TIME SYSTEM  (JST:OFT=9.D0 , UT:OFT=0.D0)
double utstart(int hr, int min, int sec, double ot);

//
//     START TIME  (ET)        EPOCH = J2000.0     (JUD-2451545.0)/36525
//
//       yr   : ORIGIN DATE  YEAR    ( 1901 =< yr =< 2099 )
//       mh   :     "        MONTH
//       dy   :     "        DAY
//       ut   : H,M,S  IN HOURS (UTC)
//       tl   : ET-UT  IN SECONDS
double etstart(int yr, int mh, int dy, double ut, double tl);

//
//     GREENWICH APPARENT SIDEREAL TIME      ( IN RADIANS )
//
//       UT   : UNIVERSAL TIME                         UNIT 1 DAY=2*PI
//       TIME : EPHEMERIS TIME       EPOCH = J2000.0   UNIT 36525 DAYS
//       tl   : ET-UT                                  UNIT SECONDS
double gast(double ut,double time,double tl);

//
//     OBLIQUITY OF THE ECLIPTIC    (IN RADIANS)
//
//     INPUT DATA    TIME : (JUD-2451545.0)/36525   EPOCH = J2000.0
//                   XT   : TIME INTERVAL           UNIT IN 36525 DAYS
//     OUTPUT DATA   EA   : COS( EPSILON )
//                   EB   : SIN( EPSILON )
int epsiln(double *ea,double *eb, double time, double xt);
#endif
