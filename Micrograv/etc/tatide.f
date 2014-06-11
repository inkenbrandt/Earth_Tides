      SUBROUTINE TATIDE(GUP,JA,JB,JC,JD,JE,JF,RM,PH,HI,TL,OT)
C
c  this tide routine taken from 
c    tideg.f, the TAMURA Gravitational Tide computation program.
c   modified to eliminate the recurssive looping for table generation,
c      renamed tatide from origional tideg (to save confusion at TFO)
c    gravimetric factor of 1.16 is added directly to this routine.
c    (in TAMURA program, 1.16 factor was multiplied external to routine.)
c
c      Jan '93, GSP.
c
c
C     THEORETICAL GRAVITY TIDE CALCULATION FOR SOLID EARTH
C
C     OUTPUT DATA
C       GUP     : UPWARD COMPONENT OF GRAVITY TIDE (UNIT IN MICRO GALS)
C     INPUT DATA
C       JA      : ORIGIN TIME  YEAR (1901 =< JA =< 2099)
C       JB      :     "        MONTH
C       JC      :     "        DAY
C       JD      :     "        HOUR 
C       JE      :     "        MINUTE
C       JF      :     "        SECOND
C       RM      : STATION PLACE  EAST LONGITUDE IN DEGREES
C       PH      :     "          NORTH LATITUDE     "
C       HI      :     "          HEIGHT         IN METERS
C       TL      : ET-UT  IN SECONDS
C       OT      : TIME SYSTEM   (JST:OT=9.D0,  UT:OT=0.D0)
C
      IMPLICIT REAL*8 (A-H,O-Z)
C
      DATA PI/3.14159 26535 89793 D0/,  RAD/0.01745 32925 19943 3D0/
      DATA FL/3.35281D-3/,GM/4.902794D12/,GS/1.327124D20/,EE/6378137.D0/
      DATA KSL,KSD,KML,KMB,KMD/16,7,61,45,43/
      DATA INI/1000/
C
C     ROUGH CHECK OF PARAMETERS
C
C      IF(JA.LE.1900 .OR. JA.GE.2100)  STOP' ERROR IN TIDEG   CHECK JA'
C      IF(JB.LE.0 .OR. JB.GE.13)       STOP' ERROR IN TIDEG   CHECK JB'
C      IF(JC.LE.0 .OR. JC.GE.32)       STOP' ERROR IN TIDEG   CHECK JC'
C      IF(JD.LT.0 .OR. JD.GE.24)       STOP' ERROR IN TIDEG   CHECK JD'
C      IF(JE.LT.0 .OR. JE.GE.60)       STOP' ERROR IN TIDEG   CHECK JE'
C      IF(JF.LT.0 .OR. JF.GE.60)       STOP' ERROR IN TIDEG   CHECK JF'
C      IF(DABS(RM).GT.180.D0)          STOP' ERROR IN TIDEG   CHECK RM'
C      IF(DABS(PH).GT. 90.D0)          STOP' ERROR IN TIDEG   CHECK PH'
C      IF(DABS(HI).GT.9999.D0)         STOP' ERROR IN TIDEG   CHECK HI'
C      IF(TL.LT.0.D0 .OR. TL.GT.99.D0) STOP' ERROR IN TIDEG   CHECK TL'
C      IF(DABS(OT).GT.12.D0)           STOP' ERROR IN TIDEG   CHECK OT'
C
C     GEOCENTRIC LATITUDE AND RADIUS
C
      RMD = RM*RAD
      GN = (FL+0.5D0*FL**2)*DSIN(2.D0*PH*RAD)
     &        -0.5D0*FL**2 *DSIN(4.D0*PH*RAD)
      PS = PH*RAD-GN
      CPS = DCOS(PS)
      SPS = DSIN(PS)
      RR = EE*(1.D0-FL*SPS**2*(1.D0+1.5D0*FL*CPS**2))+HI
C                                              UNIT IN MICRO GALS
      ZM = RR*GM*1.D8
      ZS = RR*GS*1.D8
C
C     ORIGIN TIME , no-STEP, as this is no longer a table generator!!
C
      UTST = UTSTAR(JD,JE,JF,OT)
      ETS = ETSTAR(JA,JB,JC,UTST,TL)
      UTS = UTST*PI/12.D0
      XT = 0.1D0/(24.D0*36525.D0)
      XX = 0.1D0*PI/12.D0
C
C     MAIN non-LOOP
C
        I = 1
        DMM = DFLOAT(0)
        TIME = ETS+XT*DMM
        UT = UTS+XX*DMM
C                                          COS(EPSILON), SIN(EPSILON)
      CALL EPSILN(EA,EB,TIME,XT,I,INI)
C                                          SUN'S POSITION
      SS = SUNLON(TIME,XT,KSL,I,INI)
      DS = SUNDIS(TIME,XT,KSD,I,INI)
      SSS = DSIN(SS)
      AS = DATAN2(EA*SSS,DCOS(SS))
      ES = DASIN(EB*SSS)
C                                          MOON'S POSITION 
      SM = FMOONL(TIME,XT,KML,I,INI)
      DC = FMOONB(TIME,XT,KMB,I,INI)
      DM = FMOOND(TIME,XT,KMD,I,INI)
      CDC = DCOS(DC)
      TMP = DSIN(SM)*CDC
      SDC = DSIN(DC)
      AM = DATAN2(EA*TMP-EB*SDC,CDC*DCOS(SM))
      EM = DASIN(EA*SDC+EB*TMP)
C                                          HOUR ANGLES
      HH = GAST(UT,TIME,TL)+RMD
      HM = HH-AM
      HS = HH-AS
c
c          print*,'cos obliquity of ecliptic = ',EA
c          print*,'sin obliquity of ecliptic = ',EB
c          print*,'ephemeris time                       ',TIME
c          print*,'longitude of the sun in radians =    ',SS
c          print*,'distance of the sun in meters = ',DS
c          print*,'apparent longitude moon in radians = ',SM
c          print*,'apparent latitude moon in radians = ',DC
c          print*,'geocentric distance moon in radians = ',DM
c          print*,'AS = ',AS,'   ES = ',ES
c          print*,'AM = ',AM,'   EM = ',EM
c          hhh = GAST(UT,TIME,TL)
c          print*,'Greenwich siderial time              ',hhh
c          print*,'station longitude                    ',RMD
c          print*,'GAST + station longitude =           ',HH
c          print*,'GAST + station longitude - AM = ',HM
c          print*,'GAST + station longitude - AS = ',HS
C                                          ZENITH DISTANCES
      SEM = DSIN(EM)
      SES = DSIN(ES)
      CCM = DCOS(HM)*DCOS(EM)
      CCS = DCOS(HS)*DCOS(ES)
      BM = SPS*SEM+CPS*CCM
      BS = SPS*SES+CPS*CCS
c          print*,'BM = ',BM,'   BS = ',BS
C                                          POTENTIAL
      GMX = ZM/DM**3
      GMY = GMX*RR/DM
      GMZ = GMY*RR/DM
      GSX = ZS/DS**3
c          print*,'GMX = ',GMX,'   GMY = ',GMY
c          print*,'GMZ = ',GMZ,'   GSX = ',GSX
C                                            F  UP, NORTH
      FUP = GMX*(3.D0*BM**2-1.D0)+GMY*(7.5D0*BM**3-4.5D0*BM)
     &     +GSX*(3.D0*BS**2-1.D0)+GMZ*(17.5D0*BM**4-15.D0*BM**2+1.5D0)
      FNT = (3.D0*GMX*BM+GMY*(7.5D0*BM**2-1.5D0))*(CPS*SEM-SPS*CCM)
     &     +3.D0*GSX*BS                          *(CPS*SES-SPS*CCS)
C                                          UPWARD ATTRACTION
        GUP = FUP+GN*FNT
c          print*,'FUP = ',FUP,'   FNT = ',FNT
   10 CONTINUE
C
c  multiply by gravimetric factor, 1.16
      gup = gup * 1.16d0
c
      return
      end

      DOUBLE PRECISION FUNCTION SUNLON(TIME,XT,IEN,MM,INI)
C
C     LONGITUDE OF THE SUN IN RADIANS   ( NUTATION IS TAKEN INTO ACCOUNT )
C       GRAVITY IS FREE FROM ABERRATION  (-0.0057 DEG.)
C
C       TIME : (JED-2451545.0)/36525     EPOCH = J2000.0
C       XT   : TIME INTERVAL             UNIT IN 36525 DAYS
C       IEN  : PRECISION                 ( TERMS =< 16 )
C       MM   : COUNTER
C       INI  : INTERVAL OF INITIALIZATION
C
      IMPLICIT REAL*8(A-H,O-Z)
C
      DIMENSION A(16),  B(16),  C(16)
      DIMENSION AMP(16),DIF(16),CON(16)
      save AMP, DIF, CON
C
      DATA B0/36000.7695D0/,     C0/280.4659D0/
      DATA A/19147.D-4, 200.D-4, 48.D-4, 20.D-4, 18.D-4, 18.D-4,
     &          15.D-4,  13.D-4,  7.D-4,  7.D-4,  7.D-4,  6.D-4,
     &           5.D-4,   5.D-4,  4.D-4,  4.D-4/
      DATA B/35999.050D0, 71998.1D0,  1934.D0, 32964.D0,    19.D0,
     &      445267.   D0, 45038. D0, 22519.D0, 65929.D0,  3035.D0,
     &        9038.   D0, 33718. D0,   155.D0,  2281.D0, 29930.D0,
     &       31557.   D0/
      DATA C/267.520D0, 265.1D0, 145.D0, 158.D0, 159.D0, 208.D0,
     &       254.   D0, 352. D0,  45.D0, 110.D0,  64.D0, 316.D0,
     &       118.   D0, 221. D0,  48.D0, 161.D0/
      DATA RAD/0.01745 32925 19943 3D0/
C
      SUNLON = 0.D0
C
      IF(MOD(MM-1,INI).EQ.0) THEN
C
C       INITIALIZE
C
      A(1) = 1.9147D0-0.0048D0*TIME
      DELTA = XT*0.5D0*RAD
C
      DO 20 I=1,IEN
        TEMPB = (B(I)*TIME+C(I))*RAD
        TEMPC = B(I)*DELTA
        AMP(I) = A(I)*DCOS(TEMPB)
        SUNLON = SUNLON+AMP(I)
        TEMP = 2.D0*DSIN(TEMPC)
        CON(I) = TEMP*TEMP
        DIF(I) = A(I)*TEMP*DSIN(TEMPC-TEMPB)
   20 CONTINUE
C
      ELSE
C
C       RECURRENCE FORMULA
C 
        DO 120 I=1,IEN
          DIF(I) = DIF(I)-AMP(I)*CON(I)
          AMP(I) = AMP(I)+DIF(I)
          SUNLON = SUNLON+AMP(I)
  120   CONTINUE
C
      END IF
C
      SUNLON = (SUNLON+B0*TIME+C0)*RAD
C     SUNLON = SUNLON-0.0057D0*RAD       /* CORRECTION OF ABERATION */
C
      RETURN
      END
      DOUBLE PRECISION FUNCTION SUNDIS(TIME,XT,IEN,MM,INI)
C
C     GEOCENTRIC DISTANCE OF THE SUN IN METERS
C
C       TIME : (JED-2451545.0)/36525     EPOCH = J2000.0
C       XT   : TIME INTERVAL             UNITS IN 36525 DAYS
C       IEN  : PRECISION                 ( TERMS =< 7 )
C       MM   : COUNTER
C       INI  : INTERVAL OF INITIALIZATION
C
      IMPLICIT REAL*8 (A-H,O-Z)
C
      DIMENSION A(7), B(7), C(7)
      DIMENSION AMP(7),DIF(7),CON(7)
      save AMP, DIF, CON
C
      DATA A0/1.000140D0/, CS/1.49597870D11/
      DATA A/16706.D-6, 139.D-6, 31.D-6, 16.D-6, 16.D-6, 5.D-6, 5.D-6/
      DATA B/35999.05D0, 71998.D0, 445267.D0, 32964.D0, 45038.D0,
     &       22519.  D0, 33718.D0/
      DATA C/177.53D0, 175.D0, 298.D0,  68.D0, 164.D0, 233.D0, 226.D0/
      DATA RAD/0.01745 32925 19943 3D0/
C
      AU = 0.D0
C
      IF(MOD(MM-1,INI).EQ.0) THEN
C
C       INITIALIZE
C
        DELTA = XT*0.5D0*RAD
        A(1) = 0.016706D0-0.000042D0*TIME
C
        DO 20 I=1,IEN
          TEMPB = (B(I)*TIME+C(I))*RAD
          TEMPC = B(I)*DELTA
          AMP(I) = A(I)*DCOS(TEMPB)
          AU = AU+AMP(I)
          TEMP = 2.D0*DSIN(TEMPC)
          CON(I) = TEMP*TEMP
          DIF(I) = A(I)*TEMP*DSIN(TEMPC-TEMPB)
   20   CONTINUE
C
      ELSE
C
C       RECURRENCE FORMULA
C
        DO 120 I=1,IEN
          DIF(I) = DIF(I)-AMP(I)*CON(I)
          AMP(I) = AMP(I)+DIF(I)
          AU = AU+AMP(I)
  120   CONTINUE
C
      END IF
C
      SUNDIS = (A0+AU)*CS
C
      RETURN
      END
      DOUBLE PRECISION FUNCTION FMOONL(TIME,XT,IEN,MM,INI)
C
C     APPARENT LONGITUDE OF THE MOON IN RADIANS
C
C       TIME : (JED-2451545.0)/36525          EPOCH = J2000.0
C       XT   : TIME INTERVAL                  UNIT IN 36525 DAYS
C       IEN  : PRECISION                      ( TERMS =< 61 )
C       MM   : COUNTER
C       INI  : INTERVAL OF INITIALIZATION 
C
      IMPLICIT REAL*8 (A-H,O-Z)
C
      DIMENSION A(61)  ,B(61)  ,C(61)
      DIMENSION AMP(61),DIF(61),CON(61)
      save AMP, DIF, CON
C
      DATA B0/481267.8809D0/, C0/218.3162D0/
      DATA A/62888.D-4, 12740.D-4, 6583.D-4, 2136.D-4, 1851.D-4,
     &        1144.D-4, 588.D-4, 571.D-4, 533.D-4, 458.D-4, 409.D-4,
     &         347.D-4, 304.D-4, 154.D-4, 125.D-4, 110.D-4, 107.D-4,
     &         100.D-4, 85.D-4, 79.D-4, 68.D-4, 52.D-4, 50.D-4, 40.D-4,
     &          40.D-4, 40.D-4, 38.D-4, 37.D-4, 28.D-4, 27.D-4, 26.D-4,
     &          24.D-4, 23.D-4, 22.D-4, 21.D-4, 21.D-4, 21.D-4, 18.D-4,
     &          16.D-4, 12.D-4, 11.D-4,  9.D-4,  8.D-4,  7.D-4,  7.D-4,
     &           7.D-4,  7.D-4,  6.D-4,  6.D-4,  5.D-4,  5.D-4,  5.D-4,
     &           4.D-4,  4.D-4,  3.D-4,  3.D-4,  3.D-4,  3.D-4,  3.D-4,
     &           3.D-4,  3.D-4/
      DATA B/477198.868D0,  413335.35D0, 890534.22D0, 954397.74D0,
     &        35999.05 D0,  966404.0 D0,  63863.5 D0, 377336.3 D0,
     &      1367733.1  D0,  854535.2 D0, 441199.8 D0, 445267.1 D0,
     &       513197.9D0, 75870.D0,1443603.D0, 489205.D0,1303870.D0,
     &      1431597.D0, 826671.D0, 449334.D0, 926533.D0,  31932.D0,
     &       481266.D0,1331734.D0,1844932.D0,    133.D0,1781068.D0,
     &       541062.D0,   1934.D0, 918399.D0,1379739.D0,  99863.D0,
     &       922466.D0, 818536.D0, 990397.D0,  71998.D0, 341337.D0,
     &       401329.D0,1856938.D0,1267871.D0,1920802.D0, 858602.D0,
     &      1403732.D0, 790672.D0, 405201.D0, 485333.D0,  27864.D0,
     &       111869.D0,2258267.D0,1908795.D0,1745069.D0, 509131.D0,
     &        39871.D0,  12006.D0, 958465.D0, 381404.D0, 349472.D0,
     &      1808933.D0, 549197.D0,   4067.D0,2322131.D0/
      DATA C/ 44.963D0, 10.74D0, 145.70D0, 179.93D0, 87.53D0,  276.5D0,
     &      124.2D0, 13.2D0, 280.7D0, 148.2D0, 47.4D0, 27.9D0, 222.5D0,
     &       41.D0,  52.D0, 142.D0, 246.D0, 315.D0, 111.D0, 188.D0,
     &      323.D0, 107.D0, 205.D0, 283.D0,  56.D0,  29.D0,  21.D0,
     &      259.D0, 145.D0, 182.D0,  17.D0, 122.D0, 163.D0, 151.D0,
     &      357.D0,  85.D0,  16.D0, 274.D0, 152.D0, 249.D0, 186.D0,
     &      129.D0,  98.D0, 114.D0,  50.D0, 186.D0, 127.D0,  38.D0,
     &      156.D0,  90.D0,  24.D0, 242.D0, 223.D0, 187.D0, 340.D0,
     &      354.D0, 337.D0,  58.D0, 220.D0,  70.D0, 191.D0/
      DATA RAD/0.01745 32925 19943 3D0/
C
      FMOONL = 0.D0
C
      IF (MOD(MM-1,INI).EQ.0) THEN
C
C       INITIALIZE
C
        DELTA = XT*0.5D0*RAD
C
        DO 20 I=1,IEN
          TEMPB = (B(I)*TIME+C(I))*RAD
          TEMPC = B(I)*DELTA
          AMP(I) = A(I)*DCOS(TEMPB)
          FMOONL = FMOONL+AMP(I)
          TEMP = 2.D0*DSIN(TEMPC)
          CON(I) = TEMP*TEMP
          DIF(I) = A(I)*TEMP*DSIN(TEMPC-TEMPB)
   20   CONTINUE
C
      ELSE
C
C       RECURRENCE FORMULA
C    
        DO 120 I=1,IEN
          DIF(I) = DIF(I)-AMP(I)*CON(I)
          AMP(I) = AMP(I)+DIF(I)
          FMOONL = FMOONL+AMP(I)
  120   CONTINUE
C
      END IF
C
      FMOONL = (FMOONL+B0*TIME+C0)*RAD
C
      RETURN
      END
      DOUBLE PRECISION FUNCTION FMOONB(TIME,XT,IEN,MM,INI)
C
C     APPARENT LATITUDE OF THE MOON IN RADIANS
C
C       TIME : (JED-2451545.0)/36525      EPOCH = J2000.0
C       XT   : TIME INTERVAL              UNIT IN 36525 DAYS
C       IEN  : PRECISION                  ( TERMS =< 45 )
C       MM   : COUNTER
C       INI  : INTERVAL OF INITIALIZATION
C
      IMPLICIT REAL*8 (A-H,O-Z)
C
      DIMENSION A(45)  ,B(45)  ,C(45)
      DIMENSION AMP(45),DIF(45),CON(45)
      save AMP, DIF, CON
C
      DATA A/51281.D-4, 2806.D-4, 2777.D-4, 1733.D-4, 554.D-4, 463.D-4,
     &      326.D-4,172.D-4, 93.D-4, 88.D-4, 82.D-4, 43.D-4, 42.D-4,
     &       34.D-4, 25.D-4, 22.D-4, 22.D-4, 21.D-4, 19.D-4, 18.D-4,
     &       18.D-4, 18.D-4, 15.D-4, 15.D-4, 15.D-4, 14.D-4, 13.D-4,
     &       13.D-4, 11.D-4, 10.D-4,  9.D-4,  8.D-4,  7.D-4,  6.D-4,
     &        6.D-4,  5.D-4,  5.D-4,  5.D-4,  4.D-4,  4.D-4,  3.D-4,
     &        3.D-4,  3.D-4,  3.D-4,  3.D-4/
      DATA B/483202.019D0,  960400.89D0,  6003.15D0, 407332.20D0,
     &       896537.4D0,    69866.7D0, 1373736.2D0,  1437599.8D0,
     &     884531.D0, 471196.D0, 371333.D0, 547066.D0,1850935.D0,
     &     443331.D0, 860538.D0, 481268.D0,1337737.D0, 105866.D0,
     &     924402.D0, 820668.D0, 519201.D0,1449606.D0,  42002.D0,
     &     928469.D0, 996400.D0,  29996.D0, 447203.D0,  37935.D0,
     &    1914799.D0,1297866.D0,1787072.D0, 972407.D0,1309873.D0,
     &     559072.D0,1361730.D0, 848532.D0, 419339.D0, 948395.D0,
     &    2328134.D0,1024264.D0, 932536.D0,1409735.D0,2264270.D0,
     &    1814936.D0, 335334.D0/
      DATA C/3.273D0, 138.24D0, 48.31D0, 52.43D0, 104.0D0, 82.5D0,
     &     239.0D0, 273.2D0, 187.D0, 87.D0, 55.D0, 217.D0,  14.D0,
     &     230.D0, 106.D0, 308.D0, 241.D0,  80.D0, 141.D0, 153.D0,
     &     181.D0,  10.D0,  46.D0, 121.D0, 316.D0, 129.D0,   6.D0,
     &      65.D0,  48.D0, 288.D0, 340.D0, 235.D0, 205.D0, 134.D0,
     &     322.D0, 190.D0, 149.D0, 222.D0, 149.D0, 352.D0, 282.D0,
     &      57.D0, 115.D0,  16.D0,  57.D0/
      DATA RAD/0.01745 32925 19943 3D0/
C
      FMOONB = 0.D0
C
      IF(MOD(MM-1,INI).EQ.0) THEN
C
C       INITIALIZE
C
        DELTA = XT*0.5D0*RAD
C
        DO 20 I=1,IEN
          TEMPB = (B(I)*TIME+C(I))*RAD
          TEMPC = B(I)*DELTA
          AMP(I) = A(I)*DCOS(TEMPB)
          FMOONB = FMOONB+AMP(I)
          TEMP = 2.D0*DSIN(TEMPC)
          CON(I) = TEMP*TEMP
          DIF(I) = A(I)*TEMP*DSIN(TEMPC-TEMPB)
   20   CONTINUE
C
      ELSE
C
C       RECURRENCE FORMULA
C
        DO 120 I=1,IEN
          DIF(I) = DIF(I)-AMP(I)*CON(I)
          AMP(I) = AMP(I)+DIF(I)
          FMOONB = FMOONB+AMP(I)
  120   CONTINUE
C
      END IF
C
      FMOONB = FMOONB*RAD
C
      RETURN
      END
      DOUBLE PRECISION FUNCTION FMOOND(TIME,XT,IEN,MM,INI)
C
C     GEOCENTRIC DISTANCE OF THE MOON IN METERS
C
C       TIME : (JED-2451545.0)/36525      EPOCH = J2000.0
C       XT   : TIME INTERVAL              UNIT IN 36525 DAYS
C       IEN  : PRECISION                  ( TERMS =< 43 )
C       MM   : COUNTER
C       INI  : INTERVAL OF INITIALIZATION
C
      IMPLICIT REAL*8 (A-H,O-Z)
C
      DIMENSION A(43)  ,B(43)  ,C(43)
      DIMENSION AMP(43),DIF(43),CON(43)
      save AMP, DIF, CON
C
      DATA A0/0.950725D0/
      DATA A/51820.D-6, 9530.D-6, 7842.D-6, 2824.D-6, 858.D-6, 531.D-6,
     &       400.D-6, 319.D-6, 271.D-6, 263.D-6, 197.D-6, 173.D-6,
     &       167.D-6, 111.D-6, 103.D-6,  84.D-6,  83.D-6,  78.D-6,
     &       73.D-6, 64.D-6, 63.D-6, 41.D-6, 34.D-6, 33.D-6, 31.D-6,
     &       30.D-6, 29.D-6, 26.D-6, 23.D-6, 19.D-6, 13.D-6, 13.D-6,
     &       13.D-6, 12.D-6, 11.D-6, 11.D-6, 10.D-6,  9.D-6,  7.D-6,
     &        7.D-6,  6.D-6,  6.D-6,  5.D-6/
      DATA B/477198.868D0, 413335.35D0, 890534.22D0, 954397.74D0,
     &      1367733.1D0,   854535.2D0,  377336.3D0,  441199.8D0,
     &       445267.D0, 513198.D0, 489205.D0,1431597.D0,1303870.D0,
     &        35999.D0, 826671.D0,  63864.D0, 926533.D0,1844932.D0,
     &      1781068.D0,1331734.D0, 449334.D0, 481266.D0, 918399.D0,
     &       541062.D0, 922466.D0,  75870.D0, 990397.D0, 818536.D0,
     &       553069.D0,1267871.D0,1403732.D0, 341337.D0, 401329.D0,
     &      2258267.D0,1908795.D0, 858602.D0,1745069.D0, 790672.D0,
     &      2322131.D0,1808933.D0, 485333.D0,  99863.D0, 405201.D0/
      DATA C/134.963D0, 100.74D0, 235.70D0, 269.93D0, 10.7D0, 238.2D0,
     &       103.2D0, 137.4D0, 118.D0, 312.D0, 232.D0, 45.D0, 336.D0,
     &       178.D0, 201.D0, 214.D0,  53.D0, 146.D0, 111.D0,  13.D0,
     &       278.D0, 295.D0, 272.D0, 349.D0, 253.D0, 131.D0,  87.D0,
     &       241.D0, 266.D0, 339.D0, 188.D0, 106.D0,   4.D0, 246.D0,
     &       180.D0, 219.D0, 114.D0, 204.D0, 281.D0, 148.D0, 276.D0,
     &       212.D0, 140.D0/
      DATA RAD/0.01745 32925 19943 3D0/, EE/6378137.D0/
C
      PARALX = 0.D0
C
      IF(MOD(MM-1,INI).EQ.0) THEN
C
C       INITIALIZE
C
      DELTA = XT*0.5D0*RAD
C
      DO 20 I=1,IEN
        TEMPB = (B(I)*TIME+C(I))*RAD
        TEMPC = B(I)*DELTA
        AMP(I) = A(I)*DCOS(TEMPB)
        PARALX = PARALX+AMP(I)
        TEMP = 2.D0*DSIN(TEMPC)
        CON(I) = TEMP*TEMP
        DIF(I) = A(I)*TEMP*DSIN(TEMPC-TEMPB)
  20  CONTINUE
C
      ELSE
C
C       RECURRENCE FORMULA
C
        DO 120 I=1,IEN
          DIF(I) = DIF(I)-AMP(I)*CON(I)
          AMP(I) = AMP(I)+DIF(I)
          PARALX = PARALX+AMP(I)
  120   CONTINUE
C    
      END IF
C
      PARALX = (PARALX+A0)*RAD
      FMOOND = EE/(PARALX*(1.D0-PARALX*PARALX/6.D0))
C
      RETURN
      END
      DOUBLE PRECISION FUNCTION UTSTAR(JD,JE,JF,OFT)
C
C     START TIME  (UT  IN HOURS)
C
C       JD  : HOUR
C       JE  : MINUTE
C       JF  : SECOND
C       OFT : TIME SYSTEM  (JST:OFT=9.D0 , UT:OFT=0.D0)
C
      IMPLICIT REAL*8 (A-H,O-Z)
C
      UTSTAR = DFLOAT(JD)+DFLOAT(JE)/60.D0+DFLOAT(JF)/3600.D0-OFT
C
      RETURN
      END
      DOUBLE PRECISION FUNCTION ETSTAR(JA,JB,JC,UTST,TL)
C
C     START TIME  (ET)        EPOCH = J2000.0     (JED-2451545.0)/36525
C
C       JA   : ORIGIN DATE  YEAR    ( 1901 =< JA =< 2099 )
C       JB   :     "        MONTH
C       JC   :     "        DAY
C       UTST : H,M,S  IN HOURS
C       TL   : ET-UT  IN SECONDS
C
      IMPLICIT REAL*8 (A-H,O-Z)
C
      DIMENSION M(12)
      DATA M/0,31,59,90,120,151,181,212,243,273,304,334/
C
      DAY = DFLOAT(JA*365+M(JB)+JC+JA/4-730500)-0.5D0
     &     +UTST/24.D0+TL/86400.D0
C
      IF(MOD(JA,4).EQ.0.AND.JB.LE.2) DAY=DAY-1.D0
C
      ETSTAR = DAY/36525.D0
C
      RETURN
      END
      DOUBLE PRECISION FUNCTION GAST(UT,TIME,TL)
C
C     GREENWICH APPARENT SIDEREAL TIME      ( IN RADIANS )
C
C       UT   : UNIVERSAL TIME                         UNIT 1 DAY=2*PI
C       TIME : EPHEMERIS TIME       EPOCH = J2000.0   UNIT 36525 DAYS
C       TL   : ET-UT                                  UNIT SECONDS
C
      IMPLICIT REAL*8 (A-H,O-Z)
C     
      DATA PI/3.14159 26535 89793 D0/, RAD/0.01745 32925 19943 3D0/
C
      AM = 18.69735D0+2400.05130D0*(TIME-TL/3.15576D9)
      P = 0.00029D0*DCOS((1934.D0*TIME+145.D0)*RAD)
      GAST = PI+UT+(AM+P)*PI/12.D0
C     
      RETURN
      END
      SUBROUTINE EPSILN(EA,EB,TIME,XT,MM,INI)
C
C     OBLIQUITY OF THE ECLIPTIC    (IN RADIANS)
C
C     INPUT DATA    TIME : (JED-2451545.0)/36525   EPOCH = J2000.0
C                   XT   : TIME INTERVAL           UNIT IN 36525 DAYS
C                   MM   : COUNTER
C                   INI  : INTERVAL OF INITIALIZATION
C     OUTPUT DATA   EA   : COS( EPSILON )
C                   EB   : SIN( EPSILON )
C
      IMPLICIT REAL*8 (A-H,O-Z)
C
      DATA RAD/0.01745 32925 19943 3D0/
C
      IF(MOD(MM-1,INI).EQ.0) THEN
C
C       INITIALIZE
C
        OM = (23.43928D0-0.013014D0*TIME
     &       +0.00256D0*DCOS((1934.D0*TIME+235.D0)*RAD))*RAD
        EA = DCOS(OM)
        EB = DSIN(OM)
        DOM = -(0.013014D0+0.00256D0*1934.D0*RAD
     &          *DSIN((1934.D0*TIME+235.D0)*RAD))*RAD*XT
        DEB = DSIN(DOM)
C
      ELSE
C
C       RECURRENCE FORMULA
C
        TEMP = EA-EB*DEB 
        EB = EB+EA*DEB
        EA = TEMP
C
      END IF
C
      RETURN
      END

