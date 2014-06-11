import etc
import tamura

Y=int(1999)
M=int(12)
D=int(25)
h=int(1)
m=int(1)
s=int(0)
L=float(40.759)
N=float(-111.827)
E=float(1300.0)
G=float(-7.0)
C = etc.tide(Y,M,D,h,m,s, N,L,E, 0.0, G)
print "Correction: %f"%C
C = tamura.tide(Y,M,D,h,m,s, N,L,E, 0.0, G)

print "TAMURA.PY: Correction: %f"%C
