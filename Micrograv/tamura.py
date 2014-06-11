# tamura.py - Python port of Tamura ETC F77 code
# Ugly, but it works.

from math import *

#      SUBROUTINE TATIDE(GUP,JA,JB,JC,JD,JE,JF,RM,PH,HI,TL,OFT)
#  [renamed tide() by PEG May 1999]
#
#  this tide routine taken from
#    tideg.f, the TAMURA Gravitational Tide computation program.
#   modified to eliminate the recurssive looping for table generation,
#      renamed tatide from origional tideg (to save confusion at TFO)
#    gravimetric factor of 1.16 is added directly to this routine.
#    (in TAMURA program, 1.16 factor was multiplied external to routine.)
#
#      Jan '93, GSP.
#  Converted to Python code, PEG May 1999

#
#     THEORETICAL GRAVITY TIDE CALCULATION FOR SOLID EARTH
#
#     OUTPUT DATA
#       GUP     : UPWARD COMPONENT OF GRAVITY TIDE (UNIT IN MICRO GALS)
#                 return value of 3e38 indicates bad parameters!
#     INPUT DATA
#       JA      : ORIGIN TIME  YEAR (1901 =< JA =< 2099)
#       JB      :     "        MONTH
#       JC      :     "        DAY
#       JD      :     "        HOUR
#       JE      :     "        MINUTE
#       JF      :     "        SECOND
#       RM      : STATION PLACE  EAST LONGITUDE IN DEGREES
#       PH      :     "          NORTH LATITUDE     "
#       HI      :     "          HEIGHT         IN METERS
#       TL      : ET-UT  IN SECONDS
#       OFT      : TIME SYSTEM   (JST:OFT=9.D0,  UT:OFT=0.D0)
#
#

#JA= 2013    #       JA      : ORIGIN TIME  YEAR (1901 =< JA =< 2099)
#JB= 1       #       JB      :     "        MONTH
#JC= 1       #       JC      :     "        DAY
#JD= 11      #       JD      :     "        HOUR
#JE= 0       #       JE      :     "        MINUTE
#JF= 0       #       JF      :     "        SECOND
#RM=223      #       RM      : STATION PLACE  EAST LONGITUDE IN DEGREES
#PH=40       #       PH      :     "          NORTH LATITUDE     "
#HI=1700     #       HI      :     "          HEIGHT         IN METERS
#TL=0        #       TL      : ET-UT  IN SECONDS
#OFT=9       #       OFT      : TIME SYSTEM   (JST:OFT=9.D0,  UT:OFT=0.D0)


def tide(JA, JB, JC, JD, JE, JF, RM, PH, HI, TL, OFT):
      PI= 3.141592653589793e0
      RAD = 0.0174532925199433e0
      FL=3.35281e-3
      GM=4.902794e12
      GS=1.327124e20
      EE=6378137.e0
      KSL=16
      KSD=7
      KML=61
      KMB=45
      KMD=43
#
#     ROUGH CHECK OF PARAMETERS
#
      if(JA <= 1900 or JA >= 2100):  return(3e38)
      if(JB <= 0 or JB >= 13):       return(3e38)
      if(JC <= 0 or JC >= 32):       return(3e38)
      if(JD < 0 or JD > 24):       return(3e38)
      if(JE < 0 or JE > 60):       return(3e38)
      if(JF < 0 or JF > 60):       return(3e38)
      if(abs(RM) > 180.0):          return(3e38)
      if(abs(PH) >  90.0):          return(3e38)
      if(abs(HI) > 9999.0):         return(3e38)
      if(TL < 0.0 or TL > 99.0): return(3e38)
      if(abs(OFT) > 12.0):           return(3e38)
#
#     GEOCENTRIC LATITUDE AND RADIUS
#
      RMD = RM*RAD
      GN = (FL+0.5e0*FL**2)*sin(2.0e0*PH*RAD)-0.5e0*FL**2*sin(4.0e0*PH*RAD)
      PS = PH*RAD-GN
      CPS = cos(PS)
      SPS = sin(PS)
      RR = EE*(1.0e0-FL*SPS**2*(1.0e0+1.5e0*FL*CPS**2))+HI
#                                              UNIT IN MICRO GALS
      ZM = RR*GM*1.e8
      ZS = RR*GS*1.e8
#
#     ORIGIN TIME
#
      UTST = UTSTAR(JD,JE,JF,OFT)
      ETS = ETSTAR(JA,JB,JC,UTST,TL)
      UTS = UTST*PI/12.0
      XT = 0.1/(24.0*36525.0)
      XX = 0.1*PI/12.0
#
#     MAIN PROC
#
      DMM = float(0)
      TIME = ETS+XT*DMM
      UT = UTS+XX*DMM
#                                          COS(EPSILON), SIN(EPSILON)
      (EA, EB) = EPSILN(TIME,XT)
#                                          SUN'S POSITION
      SS = SUNLON(TIME,XT,KSL)
      DS = SUNDIS(TIME,XT,KSD)
      SSS = sin(SS)
      AS = atan2(EA*SSS,cos(SS))
      ES = asin(EB*SSS)
#                                          MOON'S POSITION
      SM = FMOONL(TIME,XT,KML)
      DC = FMOONB(TIME,XT,KMB)
      DM = FMOOND(TIME,XT,KMD)
      CDC = cos(DC)
      TMP = sin(SM)*CDC
      SDC = sin(DC)
      AM = atan2(EA*TMP-EB*SDC,CDC*cos(SM))
      EM = asin(EA*SDC+EB*TMP)
#                                          HOUR ANGLES
      HH = GAST(UT,TIME,TL)+RMD
      HM = HH-AM
      HS = HH-AS
#DEBUGGING START HERE
#      print  'cos obliquity of ecliptic = %f'%EA
#      print  'sin obliquity of ecliptic = %f'%EB
#      print  'ephemeris time                       %f'%TIME
#      print  'longitude of the sun in radians =    %f'%SS
#      print  'distance of the sun in meters = %f'%DS
#      print  'apparent longitude moon in radians = %f'%SM
#      print  'apparent latitude moon in radians = %f'%DC
#      print  'geocentric distance moon in radians = %f'%DM
#      print  'AS = %f   ES = %f'%(AS,ES)
#      print  'AM = %f   EM = %f'%(AM,EM)
#      hhh = GAST(UT,TIME,TL)
#      print  'Greenwich siderial time              %f'%hhh
#      print  'station longitude                    %f'%RMD
#      print  'GAST + station longitude =           %f'%HH
#      print  'GAST + station longitude - AM = %f'%HM
#      print  'GAST + station longitude - AS = %f'%HS
#END HERE
#                                          ZENITH DISTANCES
      SEM = sin(EM)
      SES = sin(ES)
      CCM = cos(HM)*cos(EM)
      CCS = cos(HS)*cos(ES)
      BM = SPS*SEM+CPS*CCM
      BS = SPS*SES+CPS*CCS
#DEBUG
#          print*,'BM = ',BM,'   BS = ',BS
#                                          POTENTIAL
      GMX = ZM/DM**3
      GMY = GMX*RR/DM
      GMZ = GMY*RR/DM
      GSX = ZS/DS**3
#DEBUG
#          print*,'GMX = ',GMX,'   GMY = ',GMY
#          print*,'GMZ = ',GMZ,'   GSX = ',GSX
#                                            F  UP, NORTH
      FUP = GMX*(3.0*BM**2-1.0)+GMY*(7.5*BM**3-4.5*BM)+GSX*(3.0*BS**2-1.0)+GMZ*(17.5*BM**4-15.0*BM**2+1.5)
      FNT = (3.0*GMX*BM+GMY*(7.5*BM**2-1.5))*(CPS*SEM-SPS*CCM)+3.e0*GSX*BS*(CPS*SES-SPS*CCS)
#                                          UPWARD ATTRACTION
      GUP = FUP+GN*FNT
#DEBUG
#          print*,'FUP = ',FUP,'   FNT = ',FNT
#
      # 1.16 is standard ETC factor
#      GUP = GUP * 1.16
      return(GUP);


def SUNLON(TIME,XT,IEN):
#
#     LONGITUDE OF THE SUN IN RADIANS   ( NUTATION IS TAKEN INTO ACCOUNT )
#       GRAVITY IS FREE FROM ABERRATION  (-0.0057 DEG.)
#
#       TIME : (JED-2451545.0)/36525     EPOCH = J2000.0
#       XT   : TIME INTERVAL             UNIT IN 36525 DAYS
#       IEN  : PRECISION                 ( TERMS =< 16 )
#
#
      AMP=DIM(16); DIF=DIM(16); CON=DIM(16);

      B0=36000.7695
      C0=280.4659
      A=[19147.0e-4, 200.0e-4, 48.0e-4, 20.0e-4, 18.0e-4, 18.0e-4,
            15.0e-4,  13.0e-4,  7.0e-4,  7.0e-4,  7.0e-4,  6.0e-4,
             5.0e-4,   5.0e-4,  4.0e-4,  4.0e-4]
      B=[35999.050e0, 71998.1e0,  1934.e0, 32964.e0,    19.e0,
        445267.000e0, 45038.0e0, 22519.e0, 65929.e0,  3035.e0,
          9038.000e0, 33718.0e0,   155.e0,  2281.e0, 29930.e0,
         31557.000e0]
      C=[267.520e0, 265.1e0, 145.0e0, 158.0e0, 159.0e0, 208.0e0,
         254.000e0, 352.0e0,  45.0e0, 110.0e0,  64.0e0, 316.0e0,
         118.000e0, 221.0e0,  48.0e0, 161.0e0]
      RAD=0.0174532925199433

      SUNLON = 0.0
#
#       INITIALIZE
#
      A[0] = 1.9147-0.0048*TIME
      DELTA = XT*0.5*RAD

      for I in range(int(IEN)):
        TEMPB = (B[I]*TIME+C[I])*RAD
        TEMPC = B[I]*DELTA
        AMP[I] = A[I]*cos(TEMPB)
        SUNLON = SUNLON+AMP[I]
        TEMP = 2.0*sin(TEMPC)
        CON[I] = TEMP*TEMP
        DIF[I] = A[I]*TEMP*sin(TEMPC-TEMPB)
#
#       RECURRENCE FORMULA
#
#        for I in range(int(IEN)):
#          DIF[I] = DIF[I]-AMP[I]*CON[I]
#          AMP[I] = AMP[I]+DIF[I]
#          SUNLON = SUNLON+AMP[I]

      SUNLON = (SUNLON+B0*TIME+C0)*RAD

      return(SUNLON)

def SUNDIS(TIME,XT,IEN):
#
#     GEOCENTRIC DISTANCE OF THE SUN IN METERS
#
#       TIME : (JED-2451545.0)/36525     EPOCH = J2000.0
#       XT   : TIME INTERVAL             UNITS IN 36525 DAYS
#       IEN  : PRECISION                 ( TERMS =< 7 )
#
#
      A0=1.000140
      CS=1.49597870e11
      A=[16706.0e-6, 139.e-6, 31.e-6, 16.e-6, 16.e-6, 5.e-6, 5.e-6]
      B=[35999.05e0, 71998.e0, 445267.e0, 32964.e0, 45038.e0,
         22519.00e0, 33718.e0]
      C=[177.53e0, 175.e0, 298.e0,  68.e0, 164.e0, 233.e0, 226.e0]
      RAD=0.0174532925199433

      AU = 0.e0
      AMP = DIM(7); CON = DIM(7); DIF = DIM(7);
#
#       INITIALIZE
#
      DELTA = XT*0.5*RAD
      A[0] = 0.016706e0-0.000042e0*TIME

      for I in range(int(IEN)):
	TEMPB = (B[I]*TIME+C[I])*RAD
	TEMPC = B[I]*DELTA
	AMP[I] = A[I]*cos(TEMPB)
	AU = AU+AMP[I]
	TEMP = 2.e0*sin(TEMPC)
	CON[I] = TEMP*TEMP
	DIF[I] = A[I]*TEMP*sin(TEMPC-TEMPB)
#
#       RECURRENCE FORMULA
#
#      for I in range(int(IEN)):
#	DIF[I] = DIF[I]-AMP[I]*CON[I]
#	AMP[I] = AMP[I]+DIF[I]
#	AU = AU+AMP[I]
      SUNDIS = (A0+AU)*CS
      return(SUNDIS)

def FMOONL(TIME,XT,IEN):
#
#     APPARENT LONGITUDE OF THE MOON IN RADIANS
#
#       TIME : (JED-2451545.0)/36525          EPOCH = J2000.0
#       XT   : TIME INTERVAL                  UNIT IN 36525 DAYS
#       IEN  : PRECISION                      ( TERMS =< 61 )
#
#
      AMP=DIM(61); DIF=DIM(61); CON=DIM(61)
      B0=481267.8809e0
      C0=218.3162e0
      A=[62888.e-4, 12740.e-4, 6583.e-4, 2136.e-4, 1851.e-4,
          1144.e-4, 588.e-4, 571.e-4, 533.e-4, 458.e-4, 409.e-4,
           347.e-4, 304.e-4, 154.e-4, 125.e-4, 110.e-4, 107.e-4,
           100.e-4, 85.e-4, 79.e-4, 68.e-4, 52.e-4, 50.e-4, 40.e-4,
            40.e-4, 40.e-4, 38.e-4, 37.e-4, 28.e-4, 27.e-4, 26.e-4,
            24.e-4, 23.e-4, 22.e-4, 21.e-4, 21.e-4, 21.e-4, 18.e-4,
            16.e-4, 12.e-4, 11.e-4,  9.e-4,  8.e-4,  7.e-4,  7.e-4,
             7.e-4,  7.e-4,  6.e-4,  6.e-4,  5.e-4,  5.e-4,  5.e-4,
             4.e-4,  4.e-4,  3.e-4,  3.e-4,  3.e-4,  3.e-4,  3.e-4,
             3.e-4,  3.e-4]
      B=[477198.868e0,  413335.35e0, 890534.22e0, 954397.74e0,
          35999.050e0,  966404.00e0,  63863.50e0, 377336.30e0,
        1367733.100e0,  854535.20e0, 441199.80e0, 445267.10e0,
         513197.9e0, 75870.e0,1443603.e0, 489205.e0,1303870.e0,
        1431597.e0, 826671.e0, 449334.e0, 926533.e0,  31932.e0,
         481266.e0,1331734.e0,1844932.e0,    133.e0,1781068.e0,
         541062.e0,   1934.e0, 918399.e0,1379739.e0,  99863.e0,
         922466.e0, 818536.e0, 990397.e0,  71998.e0, 341337.e0,
         401329.e0,1856938.e0,1267871.e0,1920802.e0, 858602.e0,
        1403732.e0, 790672.e0, 405201.e0, 485333.e0,  27864.e0,
         111869.e0,2258267.e0,1908795.e0,1745069.e0, 509131.e0,
          39871.e0,  12006.e0, 958465.e0, 381404.e0, 349472.e0,
        1808933.e0, 549197.e0,   4067.e0,2322131.e0]
      C=[ 44.963e0, 10.74e0, 145.70e0, 179.93e0, 87.53e0,  276.5e0,
         124.2e0, 13.2e0, 280.7e0, 148.2e0, 47.4e0, 27.9e0, 222.5e0,
          41.e0,  52.e0, 142.e0, 246.e0, 315.e0, 111.e0, 188.e0,
         323.e0, 107.e0, 205.e0, 283.e0,  56.e0,  29.e0,  21.e0,
         259.e0, 145.e0, 182.e0,  17.e0, 122.e0, 163.e0, 151.e0,
         357.e0,  85.e0,  16.e0, 274.e0, 152.e0, 249.e0, 186.e0,
         129.e0,  98.e0, 114.e0,  50.e0, 186.e0, 127.e0,  38.e0,
         156.e0,  90.e0,  24.e0, 242.e0, 223.e0, 187.e0, 340.e0,
         354.e0, 337.e0,  58.e0, 220.e0,  70.e0, 191.e0]
      RAD=0.0174532925199433

      FMOONL = 0.0
#
#       INITIALIZE
#
      DELTA = XT*0.5e0*RAD
      for I in range(int(IEN)):
	TEMPB = (B[I]*TIME+C[I])*RAD
	TEMPC = B[I]*DELTA
	AMP[I] = A[I]*cos(TEMPB)
	FMOONL = FMOONL+AMP[I]
	TEMP = 2.e0*sin(TEMPC)
	CON[I] = TEMP*TEMP
	DIF[I] = A[I]*TEMP*sin(TEMPC-TEMPB)
#
#       RECURRENCE FORMULA
#
#      for I in range(int(IEN)):
#	DIF[I] = DIF[I]-AMP[I]*CON[I]
#	AMP[I] = AMP[I]+DIF[I]
#	FMOONL = FMOONL+AMP[I]
      FMOONL = (FMOONL+B0*TIME+C0)*RAD
      return(FMOONL)

def FMOONB(TIME,XT,IEN):
#
#     APPARENT LATITUDE OF THE MOON IN RADIANS
#
#       TIME : (JED-2451545.0)/36525      EPOCH = J2000.0
#       XT   : TIME INTERVAL              UNIT IN 36525 DAYS
#       IEN  : PRECISION                  ( TERMS =< 45 )
#       MM   : COUNTER
#       INI  : INTERVAL OF INITIALIZATION
#
      AMP=DIM(45); DIF=DIM(45); CON=DIM(45)

      A=[51281.e-4, 2806.e-4, 2777.e-4, 1733.e-4, 554.e-4, 463.e-4,
           326.e-4,172.e-4, 93.e-4, 88.e-4, 82.e-4, 43.e-4, 42.e-4,
            34.e-4, 25.e-4, 22.e-4, 22.e-4, 21.e-4, 19.e-4, 18.e-4,
            18.e-4, 18.e-4, 15.e-4, 15.e-4, 15.e-4, 14.e-4, 13.e-4,
            13.e-4, 11.e-4, 10.e-4,  9.e-4,  8.e-4,  7.e-4,  6.e-4,
             6.e-4,  5.e-4,  5.e-4,  5.e-4,  4.e-4,  4.e-4,  3.e-4,
             3.e-4,  3.e-4,  3.e-4,  3.e-4]
      B=[483202.019e0,  960400.89e0,  6003.15e0, 407332.20e0,
         896537.4e0,    69866.7e0, 1373736.2e0,  1437599.8e0,
         884531.e0, 471196.e0, 371333.e0, 547066.e0,1850935.e0,
         443331.e0, 860538.e0, 481268.e0,1337737.e0, 105866.e0,
         924402.e0, 820668.e0, 519201.e0,1449606.e0,  42002.e0,
         928469.e0, 996400.e0,  29996.e0, 447203.e0,  37935.e0,
        1914799.e0,1297866.e0,1787072.e0, 972407.e0,1309873.e0,
         559072.e0,1361730.e0, 848532.e0, 419339.e0, 948395.e0,
        2328134.e0,1024264.e0, 932536.e0,1409735.e0,2264270.e0,
        1814936.e0, 335334.e0]
      C=[3.273e0, 138.24e0, 48.31e0, 52.43e0, 104.0e0, 82.5e0,
       239.0e0, 273.2e0, 187.e0, 87.e0, 55.e0, 217.e0,  14.e0,
       230.e0, 106.e0, 308.e0, 241.e0,  80.e0, 141.e0, 153.e0,
       181.e0,  10.e0,  46.e0, 121.e0, 316.e0, 129.e0,   6.e0,
        65.e0,  48.e0, 288.e0, 340.e0, 235.e0, 205.e0, 134.e0,
       322.e0, 190.e0, 149.e0, 222.e0, 149.e0, 352.e0, 282.e0,
        57.e0, 115.e0,  16.e0,  57.e0]
      RAD=0.0174532925199433

      FMOONB = 0.0
#
#       INITIALIZE
#
      DELTA = XT*0.5e0*RAD
      for I in range(int(IEN)):
	TEMPB = (B[I]*TIME+C[I])*RAD
	TEMPC = B[I]*DELTA
	AMP[I] = A[I]*cos(TEMPB)
	FMOONB = FMOONB+AMP[I]
	TEMP = 2.e0*sin(TEMPC)
	CON[I] = TEMP*TEMP
	DIF[I] = A[I]*TEMP*sin(TEMPC-TEMPB)
#
#       RECURRENCE FORMULA
#
#      for I in range(int(IEN)):
#	DIF[I] = DIF[I]-AMP[I]*CON[I]
#	AMP[I] = AMP[I]+DIF[I]
#	FMOONB = FMOONB+AMP[I]
      FMOONB = FMOONB*RAD
      return(FMOONB)

def FMOOND(TIME,XT,IEN):
#
#     GEOCENTRIC DISTANCE OF THE MOON IN METERS
#
#       TIME : (JED-2451545.0)/36525      EPOCH = J2000.0
#       XT   : TIME INTERVAL              UNIT IN 36525 DAYS
#       IEN  : PRECISION                  ( TERMS =< 43 )
#       MM   : COUNTER
#       INI  : INTERVAL OF INITIALIZATION
#
      AMP=DIM(43); DIF=DIM(43); CON=DIM(43)
      A0=0.950725e0
      A=[51820.e-6, 9530.e-6, 7842.e-6, 2824.e-6, 858.e-6, 531.e-6,
           400.e-6, 319.e-6, 271.e-6, 263.e-6, 197.e-6, 173.e-6,
           167.e-6, 111.e-6, 103.e-6,  84.e-6,  83.e-6,  78.e-6,
            73.e-6, 64.e-6, 63.e-6, 41.e-6, 34.e-6, 33.e-6, 31.e-6,
            30.e-6, 29.e-6, 26.e-6, 23.e-6, 19.e-6, 13.e-6, 13.e-6,
            13.e-6, 12.e-6, 11.e-6, 11.e-6, 10.e-6,  9.e-6,  7.e-6,
             7.e-6,  6.e-6,  6.e-6,  5.e-6]
      B=[477198.868e0, 413335.35e0, 890534.22e0, 954397.74e0,
        1367733.1e0,   854535.2e0,  377336.3e0,  441199.8e0,
         445267.e0, 513198.e0, 489205.e0,1431597.e0,1303870.e0,
          35999.e0, 826671.e0,  63864.e0, 926533.e0,1844932.e0,
        1781068.e0,1331734.e0, 449334.e0, 481266.e0, 918399.e0,
         541062.e0, 922466.e0,  75870.e0, 990397.e0, 818536.e0,
         553069.e0,1267871.e0,1403732.e0, 341337.e0, 401329.e0,
        2258267.e0,1908795.e0, 858602.e0,1745069.e0, 790672.e0,
        2322131.e0,1808933.e0, 485333.e0,  99863.e0, 405201.e0]
      C=[134.963e0, 100.74e0, 235.70e0, 269.93e0, 10.7e0, 238.2e0,
         103.2e0, 137.4e0, 118.e0, 312.e0, 232.e0, 45.e0, 336.e0,
         178.e0, 201.e0, 214.e0,  53.e0, 146.e0, 111.e0,  13.e0,
         278.e0, 295.e0, 272.e0, 349.e0, 253.e0, 131.e0,  87.e0,
         241.e0, 266.e0, 339.e0, 188.e0, 106.e0,   4.e0, 246.e0,
         180.e0, 219.e0, 114.e0, 204.e0, 281.e0, 148.e0, 276.e0,
         212.e0, 140.e0]
      RAD=0.0174532925199433
      EE=6378137.0

      PARALX = 0.e0
#
#       INITIALIZE
#
      DELTA = XT*0.5e0*RAD

      for I in range(int(IEN)):
        TEMPB = (B[I]*TIME+C[I])*RAD
        TEMPC = B[I]*DELTA
        AMP[I] = A[I]*cos(TEMPB)
        PARALX = PARALX+AMP[I]
        TEMP = 2.e0*sin(TEMPC)
        CON[I] = TEMP*TEMP
        DIF[I] = A[I]*TEMP*sin(TEMPC-TEMPB)
#
#       RECURRENCE FORMULA
#
#      for I in range(int(IEN)):
#	DIF[I] = DIF[I]-AMP[I]*CON[I]
#	AMP[I] = AMP[I]+DIF[I]
#	PARALX = PARALX+AMP[I]
      PARALX = (PARALX+A0)*RAD
      FMOOND = EE/(PARALX*(1.0-PARALX*PARALX/6.0))
      return(FMOOND)

def UTSTAR(JD,JE,JF,OFT):
#
#     START TIME  (UT  IN HOURS)
#
#       JD  : HOUR
#       JE  : MINUTE
#       JF  : SECOND
#       OFT : TIME SYSTEM  (JST:OFT=9.D0 , UT:OFT=0.D0)
#
      UTSTAR = float(JD)+float(JE)/60.e0+float(JF)/3600.e0-OFT
      return(UTSTAR)

def ETSTAR(JA,JB,JC,UTST,TL):
#
#     START TIME  (ET)        EPOCH = J2000.0     (JED-2451545.0)/36525
#
#       JA   : ORIGIN DATE  YEAR    ( 1901 =< JA =< 2099 )
#       JB   :     "        MONTH
#       JC   :     "        DAY
#       UTST : H,M,S  IN HOURS
#       TL   : ET-UT  IN SECONDS
#
      M=[0,31,59,90,120,151,181,212,243,273,304,334]
      DAY = float(JA*365.0+M[int(JB)-1]+JC+JA/4-730500)-0.5e0+UTST/24.e0+TL/86400.e0
      if(JA % 4 == 0 and JB <= 2): DAY=DAY-1.e0
      ETSTAR = DAY/36525.e0
      return(ETSTAR)

def GAST(UT,TIME,TL):
#
#     GREENWICH APPARENT SIDEREAL TIME      ( IN RADIANS )
#
#       UT   : UNIVERSAL TIME                         UNIT 1 DAY=2*PI
#       TIME : EPHEMERIS TIME       EPOCH = J2000.0   UNIT 36525 DAYS
#       TL   : ET-UT                                  UNIT SECONDS
#
      PI=3.141592653589793
      RAD=0.0174532925199433
      AM = 18.69735e0+2400.05130e0*(TIME-TL/3.15576e9)
      P = 0.00029e0*cos((1934.e0*TIME+145.e0)*RAD)
      GAST = PI+UT+(AM+P)*PI/12.e0
      return(GAST)

def EPSILN(TIME,XT):
#
#     OBLIQUITY OF THE ECLIPTIC    (IN RADIANS)
#
#     INPUT DATA    TIME : (JED-2451545.0)/36525   EPOCH = J2000.0
#                   XT   : TIME INTERVAL           UNIT IN 36525 DAYS
#     OUTPUT DATA   EA   : COS( EPSILON )
#                   EB   : SIN( EPSILON )
#
      RAD=0.0174532925199433
#
#       INITIALIZE
#
      OM = (23.43928e0-0.013014e0*TIME+0.00256e0*cos((1934.e0*TIME+235.e0)*RAD))*RAD
      EA = cos(OM)
      EB = sin(OM)
      DOM = -(0.013014e0+0.00256e0*1934.e0*RAD*sin((1934.e0*TIME+235.e0)*RAD))*RAD*XT
      DEB = sin(DOM)
#
#       RECURRENCE FORMULA
#
#      TEMP = EA-EB*DEB
#      EB = EB+EA*DEB
#      EA = TEMP
#
      return(EA, EB)


def DIM(size):
  # create an array of zeros size entries long and return it
  array = []
  for i in range(size):
    array.append(0.000e0)
  return(array)
