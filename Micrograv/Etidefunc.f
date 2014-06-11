C
C  This main program is designed to call two subroutines by J.C. Harrison
C  which generate various types of tides vs time for any point on the
C  Earth's surface.  The generation of earth-strain tides using the Love
C  numbers is approximate, assuming homogeneous/isotropic surface materials
C  with no account for local topographic effects.
C
C_______________________________________________________________________________
C
      double precision function FirstHorzTideStrain3
     +      (ETime,Slat,Slong,Salt,Azim)

      IMPLICIT REAL*8(A-H,O-Z),INTEGER*4(I-N)
      DIMENSION ASTRON(12)
c
      call Ntide1(ETime,Astron)
c  3 - first component of horizontal strain tide along given azimuth.
      Kind = 3
      ETC = Tid2(Slat,Slong,Salt,KIND,Azim,astron)
	FirstHorzTideStrain3 = ETC
c
	return
	end
C
C_______________________________________________________________________________
C
      double precision function SecondHorzTideStrain4
     +                        (ETime,Slat,Slong,Salt)

      IMPLICIT REAL*8(A-H,O-Z),INTEGER*4(I-N)
      DIMENSION ASTRON(12)
c
      call Ntide1(ETime,Astron)
c  4 - second component of horizontal strain tide
      Kind = 4
      Azim = 0.0D0
      ETC = Tid2(Slat,Slong,Salt,KIND,Azim,astron)
	SecondHorzTideStrain4 = ETC
c
	return
	end
C
C_______________________________________________________________________________
C
      double precision function GravityTide6(ETime,Slat,Slong,Salt)

      IMPLICIT REAL*8(A-H,O-Z),INTEGER*4(I-N)
      DIMENSION ASTRON(12)
c
      call Ntide1(ETime,Astron)
c  6 - gravity tide in microgals, ref. earth ellipsoid.
      Kind = 6
      Azim = 0.0D0
      ETC = Tid2(Slat,Slong,Salt,KIND,Azim,astron)
	GravityTide6 = ETC
c
	return
	end
C
C_______________________________________________________________________________
C
      double precision function TiltTide7(ETime,Slat,Slong,Salt)

      IMPLICIT REAL*8(A-H,O-Z),INTEGER*4(I-N)
      DIMENSION ASTRON(12)
c
      call Ntide1(ETime,Astron)
c  7 - tilt tide in nanoradians, ref. earth ellipsoid.
      Kind = 7
      Azim = 0.0D0
      ETC = Tid2(Slat,Slong,Salt,KIND,Azim,astron)
	TiltTide7 = ETC
c
	return
	end
C
C_______________________________________________________________________________
C
      double precision function DryTide8(ETime,Slat,Slong,Salt)

      IMPLICIT REAL*8(A-H,O-Z),INTEGER*4(I-N)
      DIMENSION ASTRON(12)
c
      call Ntide1(ETime,Astron)
c  8 - dry tidal dilatation in ppb.
      Kind = 8
      Azim = 0.0D0
      ETC = Tid2(Slat,Slong,Salt,KIND,Azim,astron)
	DryTide8 = ETC
c
	return
	end
C
C_______________________________________________________________________________
C
      double precision function ShearTide9(ETime,Slat,Slong,Salt)

      IMPLICIT REAL*8(A-H,O-Z),INTEGER*4(I-N)
      DIMENSION ASTRON(12)
c
      call Ntide1(ETime,Astron)
c  9 - e theta lambda, shear component of n-s and e-w strain.
      Kind = 9
      Azim = 0.0D0
      ETC = Tid2(Slat,Slong,Salt,KIND,Azim,astron)
	ShearTide9 = ETC
c
	return
	end
C
C_______________________________________________________________________________
C
      SUBROUTINE Ntide1(ETime,Astron)
      IMPLICIT REAL*8(A-H,O-Z),INTEGER*4(I-N)
      DIMENSION ASTRON(12)
      REAL*8 NOSTRA
c
      DATA R/57.295779513082321D0/
      DATA RC1,GM,GS/6.68449E-14,4.90287E18,1.32718E26/
c
      DT = 42.0D0 / 86400.0D0
C   CONVERSION TO EPHEMERIS TIME BY ADDING 24 SECS.....
      T  = (ETime - 1.5 + DT) / 36525.0D0
      W  = (23.45229D0-0.01301D0*T)/R
      SINW=SIN(W)
      COSW=COS(W)
      E1 = 0.01675104D0 - 0.0000418D0*T
      T2 = T*T
      T3 = T2*T
      S  =(270.43416D0+481267.88314D0*T-0.00113D0*T2)/R
      H  =(279.69668D0+36000.76892D0*T+0.0003D0*T2)/R
      P  =(334.32956D0+4069.03403D0*T-0.01032D0*T2-0.00001D0*T3)/R
      PS =(281.22083D0+1.71918D0*T+0.00045D0*T2)/R
      AN =(259.18328D0-1934.14201D0*T+0.00208D0*T2)/R
C   BL BLS BF BD ARE THE FUNDAMENTAL ARGUMENTS OF BROWNS THEORY
      BL = S-P
      BLS= H-PS
      BF = S-AN
      BD = S-H
C   LUNAR LAT LONG AND PARALLAX FROM BROWN. LATTER TWO FROM
C   IMPROVED LUNAR EPHEMERMIS, LATITUDE FROM RAS PAPER OF 1908....
      TLONGM=S+0.10976*SIN(BL)-0.02224*SIN(BL-2.*BD)+0.01149*SIN(2.*BD)+
     +        0.00373*SIN(2.*BL) - 0.00324*SIN(BLS)-0.00200*SIN(2.*BF)-
     +        0.00103*SIN(2.*BL-2.*BD) - 0.00100*SIN(BL+BLS-2.*BD) +
     +        0.00093*SIN(BL+2.*BD) - 0.00080*SIN(BLS-2.*BD) +
     +        0.00072*SIN(BL-BLS)-0.00061*SIN(BD)-0.00053*SIN(BL+BLS)
      TLONGS = H+2.*E1*SIN(H-PS)+1.25*E1**2*SIN(2.*(H-PS))
      TLATM = 0.08950*SIN(BF) + 0.00490*SIN(BL+BF) -
     +        0.00485*SIN(BF-BL) - 0.00303*SIN(BF-2.*BD) +
     +        0.00097*SIN(2.*BD+BF-BL) - 0.00081*SIN(BL+BF-2.*BD) +
     +        0.00057*SIN(BF+2.*BD)
      RDM   =(3422.45+186.54*COS(BL) + 34.31*COS(BL-2.*BD) +
     +       28.23*COS(2.*BD) + 10.17*COS(2.*BL) + 3.09*COS(BL+2.*BD) +
     +       1.92*COS(BLS-2.*BD) + 1.44*COS(BL+BLS-2.*BD) +
     +       1.15*COS(BL-BLS) - 0.98*COS(BD) - 0.95*COS(BL+BLS) -
     +       0.71*COS(BL-2.*BF) + 0.62*COS(3.*BL) + 0.60*COS(BL-4.*BD))
     +       / 1.31559E14
      RDS   = RC1*(1.+E1*COS(H-PS) + 0.00028*COS(2.*(H-PS)))
      CONSTS = GS*(RDS**3)
      CONSTM = GM*(RDM**3)
      SINMLAT= SIN(TLATM)
      COSMLAT= COS(TLATM)
      SINMLNG= SIN(TLONGM)
      COSMLNG= COS(TLONGM)
      SINSLNG= SIN(TLONGS)
      COSSLNG= COS(TLONGS)
C   CONVERT FROM CELESTIAL LAT AND LONG ACCORDING TO EXPLAN SUPPL OF
C   NA AND LE PAGE 26
      COSPAS = SINSLNG*SINW
      SINPAS = (1.0-COSPAS**2)**0.5
      ATS    = SINSLNG*COSW
      RAS    = ATAN2(ATS,COSSLNG)
      COSPAM = COSMLAT*SINMLNG*SINW+SINMLAT*COSW
      SINPAM = (1.0-COSPAM**2)**0.5
      AT1    = COSMLAT*SINMLNG*COSW-SINMLAT*SINW
      AT2    = COSMLAT*COSMLNG
      RAM    = ATAN2(AT1,AT2)
c      RAGM   = (15.*(HR-12.))/R+H     'delta = 0
      Daily  = ETime - Int(ETime) - 0.5
      RAGM = 360.0 * Daily / R + H
      TELS   = RAS-RAGM
      TELM   = RAM-RAGM
      SINTELS= SIN(TELS)
      COSTELS= COS(TELS)
      SINTELM= SIN(TELM)
      COSTELM= COS(TELM)
      S2TELS = 2.*SINTELS*COSTELS
      C2TELS = COSTELS**2-SINTELS**2
      S2TELM = 2.*SINTELM*COSTELM
      C2TELM = COSTELM**2-SINTELM**2
C   END OF OPTIONAL ASTRONOMICAL PRINTOUT.......
      ASTRON(1) = 0.25*CONSTS* (3.*COSPAS**2-1.) +
     +   0.25*CONSTM*(3.*COSPAM**2-1.)
      CASA   = 3.*CONSTS*SINPAS*COSPAS
      NOSTRA = 3.*CONSTM*SINPAM*COSPAM
      ASTRON(2) = CASA*COSTELS+NOSTRA*COSTELM
      ASTRON(3) = CASA*SINTELS+NOSTRA*SINTELM
      CASA        = 0.75*CONSTS*SINPAS**2
      NOSTRA      = 0.75*CONSTM*SINPAM**2
      ASTRON(4) = CASA*C2TELS+NOSTRA*C2TELM
      ASTRON(5) = CASA*S2TELS+NOSTRA*S2TELM
      CONSTM    = CONSTM*RDM
      ASTRON(6) = 0.25*CONSTM*(5.*COSPAM**3-3.*COSPAM)
      NOSTRA    = 0.375*SINPAM*(5.*COSPAM**2-1.)*CONSTM
      ASTRON(7) = NOSTRA*COSTELM
      ASTRON(8) = NOSTRA*SINTELM
      NOSTRA    = 3.75*CONSTM*SINPAM**2*COSPAM
      ASTRON(9) = NOSTRA*C2TELM
      ASTRON(10)= NOSTRA*S2TELM
      NOSTRA    = 0.625*(SINPAM**3)*CONSTM
      ASTRON(11)= NOSTRA*(4.*COSTELM**3-3.*COSTELM)
      ASTRON(12)= NOSTRA*(3.*SINTELM-4.*SINTELM**3)
c
      RETURN
      END
C
c____________________________________________________________
C
      function Tid2(SLAT,SLONG,SH,KIND,ALPHA,astron)
      IMPLICIT REAL*8(A-H,O-Z),INTEGER*4(I-N)
      DIMENSION ASTRON(12),TIDE(12)
      DIMENSION GEOG(12)
      DATA R/57.295779513082321D0/
c
      SLATR=SLAT/R
      DEL=.00337D0*SIN(2.*SLATR)
      SLATR=SLATR-DEL
      CSPA=SIN(SLATR)
      SNPA=COS(SLATR)
      SNLNG=SIN(SLONG/R)
      CSLNG=COS(SLONG/R)
      CSALF=COS(ALPHA/R)
      SNALF=SIN(ALPHA/R)
      C2LNG=CSLNG**2-SNLNG**2
      S2LNG=2.*SNLNG*CSLNG
      CPA2=CSPA**2
      SPA2=SNPA**2
      SNCSPA=SNPA*CSPA
      A1=CSALF**2
      A2=SNALF**2
      A3=CSALF*SNALF
      C3LNG=4.*CSLNG**3-3.*CSLNG
      S3LNG=3.*SNLNG-4.*SNLNG**3
      RSTA=6.378160E8*(1.-.003353*CSPA**2)+100.*SH
      GO TO(1,2,3,4,5,6,7,9,9),KIND
    1 GEOG(1)=3.*CPA2-1.
      GEOG(2)=SNCSPA*CSLNG
      GEOG(3)=SNCSPA*SNLNG
      GEOG(4)=SPA2*C2LNG
      GEOG(5)=SPA2*S2LNG
      GEOG(6)=5.*CSPA**3-3.*CSPA
      GEOG(7)=SNPA*(5.*CPA2-1.)*CSLNG
      GEOG(8)=SNPA*(5.*CPA2-1.)*SNLNG
      GEOG(9)=SPA2*CSPA*C2LNG
      GEOG(10)=SPA2*CSPA*S2LNG
      GEOG(11)=SNPA**3*C3LNG
      GEOG(12)=SNPA**3*S3LNG
      A=-2.*RSTA*10**6
      B=-3.*RSTA**2*10**6
      GO TO 10
    2 GEOG(1)=6.*SNCSPA*CSALF
      GEOG(2)=-(CPA2-SPA2)*CSLNG*CSALF-CSPA*SNLNG*SNALF
      GEOG(3)=-(CPA2-SPA2)*SNLNG*CSALF+CSPA*CSLNG*SNALF
      GEOG(4)=-2.*SNCSPA*C2LNG*CSALF-2.*SNPA*S2LNG*SNALF
      GEOG(5)=-2.*SNCSPA*S2LNG*CSALF+2.*SNPA*C2LNG*SNALF
      GEOG(6)=-3.*SNPA*(1.-5.*CPA2)*CSALF
      GEOG(7)=-CSPA*(5.*(CPA2-2.*SPA2)-1.)*CSLNG*CSALF-(5.*CPA2-1.
     X)*SNLNG*SNALF
      GEOG(8)=-CSPA*(5.*(CPA2-2.*SPA2)-1.)*SNLNG*CSALF+(5.*CPA2-1.
     X)*CSLNG*SNALF
      GEOG(9)=-SNPA*(2.*CPA2-SPA2)*C2LNG*CSALF-2.*SNCSPA*S2LNG*SNALF
      GEOG(10)=-SNPA*(2.*CPA2-SPA2)*S2LNG*CSALF+2.*SNCSPA*C2LNG*SNALF
      GEOG(11)=-3.*SPA2*CSPA*C3LNG*CSALF-3.*SPA2*S3LNG*SNALF
      GEOG(12)=-3.*SPA2*CSPA*S3LNG*CSALF+3.*SPA2*C3LNG*SNALF
      A=RSTA*10**9/979.8
      B=RSTA*A
      GO TO 10
    3 GEOG(1)=-6.*(CPA2-SPA2)*A1-6.*CPA2*A2
      GEOG(2)=-4.*SNCSPA*CSLNG*A1-2.*SNCSPA*CSLNG*A2+2.*SNPA*SNLNG*A3
      GEOG(3)=-4.*SNCSPA*SNLNG*A1-2.*SNCSPA*SNLNG*A2-2.*SNPA*CSLNG*A3
      GEOG(4)=2.*(CPA2-SPA2)*C2LNG*A1+2.*C2LNG*(CPA2-2.)
     1*A2-4.*CSPA*S2LNG*A3
      GEOG(5)=2.*(CPA2-SPA2)*S2LNG*A1+2.*S2LNG*(CPA2-2.)*A2+4.*CSPA*
     1C2LNG*A3
      GEOG(6)=(30.*CSPA*SPA2-15.*CSPA*CPA2+3.*CSPA)*A1+3.*CSPA*(1.-
     15.*CPA2)*A2
      GEOG(7)=SNPA*(15.*SPA2-14.)*CSLNG*A2+SNPA*(45.*SPA2-34.)*CSLNG*A1
     1+20.*SNCSPA*SNLNG*A3
      GEOG(8)=SNPA*(15.*SPA2-14.)*SNLNG*A2+SNPA*(45.*SPA2-34.)*SNLNG*
     1A1-20.*SNCSPA*CSLNG*A3
      GEOG(9)=CSPA*C2LNG*(2.*CPA2-7.*SPA2)*A1+CSPA*C2LNG*(2.*CPA2-
     1SPA2-4.)*A2+4.*S2LNG*(SPA2-CPA2)*A3
      GEOG(10)=CSPA*S2LNG*(2.*CPA2-7.*SPA2)*A1+CSPA*S2LNG*(2.*CPA2-
     1SPA2-4.)*A2+4.*C2LNG*(CPA2-SPA2)*A3
      GEOG(11)=SNPA*C3LNG*(6.*CPA2-3.*SPA2)*A1+3.*SNPA*C3LNG*(CPA2-
     13.)*A2-12.*SNCSPA*S3LNG*A3
      GEOG(12)=SNPA*S3LNG*(6.*CPA2-3.*SNPA)*A1+3.*SNPA*S3LNG*(CPA2-
     13.)*A2+12.*SNCSPA*C3LNG*A3
      A=RSTA*10**9/979.8
      B=RSTA*A
      GO TO 10
    4 GEOG(1)=3.*CPA2-1.
      GEOG(2)=SNCSPA*CSLNG
      GEOG(3)=SNCSPA*SNLNG
      GEOG(4)=SPA2*C2LNG
      GEOG(5)=SPA2*S2LNG
      GEOG(6)=5.*CSPA**3-3.*CSPA
      GEOG(7)=SNPA*(5.*CPA2-1.)*CSLNG
      GEOG(8)=SNPA*(5.*CPA2-1.)*SNLNG
      GEOG(9)=SPA2*CSPA*C2LNG
      GEOG(10)=SPA2*CSPA*S2LNG
      GEOG(11)=SNPA**3*C3LNG
      GEOG(12)=SNPA**3*S3LNG
      A=RSTA*10**9/979.8
      B=RSTA*A
      GO TO 10
    5 GEOG(1)=3.*CPA2-1.
      GEOG(2)=SNCSPA*CSLNG
      GEOG(3)=SNCSPA*SNLNG
      GEOG(4)=SPA2*C2LNG
      GEOG(5)=SPA2*S2LNG
      GEOG(6)=5.*CSPA**3-3.*CSPA
      GEOG(7)=SNPA*(5.*CPA2-1.)*CSLNG
      GEOG(8)=SNPA*(5.*CPA2-1.)*SNLNG
      GEOG(9)=SPA2*CSPA*C2LNG
      GEOG(10)=SPA2*CSPA*S2LNG
      GEOG(11)=SNPA**3*C3LNG
      GEOG(12)=SNPA*3**S3LNG
      A=RSTA**2
      B=A*RSTA
      GO TO 10
    6 GEOG(1)=-2.*(3.*CPA2-1.)-DEL*6.*SNCSPA
      GEOG(2)=(-2.*SNCSPA+DEL*(CPA2-SPA2))*CSLNG
      GEOG(3)=(-2.*SNCSPA+DEL*(CPA2-SPA2))*SNLNG
      GEOG(4)=(-2.*SPA2+DEL*(2.*SNCSPA))*C2LNG
      GEOG(5)=(-2.*SPA2+DEL*(2.*SNCSPA))*S2LNG
      GEOG(6)=5.*CSPA**3-3.*CSPA
      GEOG(7)=SNPA*(5.*CPA2-1.)*CSLNG
      GEOG(8)=SNPA*(5.*CPA2-1.)*SNLNG
      GEOG(9)=SPA2*CSPA*C2LNG
      GEOG(10)=SPA2*CSPA*S2LNG
      GEOG(11)=SNPA**3*C3LNG
      GEOG(12)=SNPA**3*S3LNG
      A=RSTA*10**6
      B=-3.*RSTA**2*10**6
      GO TO 10
    7 GEOG(1)=(6.*SNCSPA-DEL*2.*(3.*CPA2-1.))*CSALF
      GEOG(2)=(-(CPA2-SPA2)-DEL*2.*SNCSPA)*CSLNG*CSALF-CSPA*SNLNG*SNALF
      GEOG(3)=(-(CPA2-SPA2)-DEL*2.*SNCSPA)*SNLNG*CSALF+CSPA*CSLNG*SNALF
      GEOG(4)=(-2.*SNCSPA-DEL*2.*SPA2)*C2LNG*CSALF-2.*SNPA*S2LNG*SNALF
      GEOG(5)=(-2.*SNCSPA-DEL*2.*SPA2)*S2LNG*CSALF+2.*SNPA*C2LNG*SNALF
      GEOG(6)=-3.*SNPA*(1.-5.*CPA2)*CSALF
      GEOG(7)=-CSPA*(5.*(CPA2-2.*SPA2)-1.)*CSLNG*CSALF-(5.*CPA2-1.
     X)*SNLNG*SNALF
      GEOG(8)=-CSPA*(5.*(CPA2-2.*SPA2)-1.)*SNLNG*CSALF+(5.*CPA2-1.
     X)*CSLNG*SNALF
      GEOG(9)=-SNPA*(2.*CPA2-SPA2)*C2LNG*CSALF-2.*SNCSPA*S2LNG*SNALF
      GEOG(10)=-SNPA*(2.*CPA2-SPA2)*S2LNG*CSALF+2.*SNCSPA*C2LNG*SNALF
      GEOG(11)=-3.*SPA2*CSPA*C3LNG*CSALF-3.*SPA2*S3LNG*SNALF
      GEOG(12)=-3.*SPA2*CSPA*S3LNG*CSALF+3.*SPA2*C3LNG*SNALF
      A=RSTA*10**9/979.8
      B=RSTA*A
      GO TO 10
   9  GEOG(1)=0
      GEOG(2)=2.*SNPA*SNLNG
      GEOG(3)=-2.*SNPA*CSLNG
      GEOG(4)=-4.*CSPA*S2LNG
      GEOG(5)=4.*CSPA*C2LNG
      GEOG(6)=0.00
      GEOG(7)=20.*SNCSPA*SNLNG
      GEOG(8)=-20.*SNCSPA*CSLNG
      GEOG(9)=4.*(SPA2-CPA2)*S2LNG
      GEOG(10)=+4.*(CPA2-SPA2)*C2LNG
      GEOG(11)=-12.*SNCSPA*S3LNG
      GEOG(12)=12.*SNCSPA*C3LNG
      A=RSTA*10**9/979.8
      B=A*RSTA
   10 CONTINUE
c
      SUM=0.
      DO J = 1,12
	  RM = A
	  if( J.ge.6) RM = B
        TIDE(J) = RM * GEOG(J)*ASTRON(J)
        SUM = SUM + TIDE(J)
      enddo
c
      Tid2 = SUM
c
      RETURN
      END
