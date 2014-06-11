#!/usr/bin/python
# compute new sensitivity from formulae in manual
import math

print "Tilt Sensitivity Calculator"
print "X1 refers to the tilt measurement, in arc sec"
print "R0/R1 refer to the gravimeter readings, in mGal"
print "Get the current tilt sensitivity from data files or the Setup menu"
oldSens = float(raw_input("Current tilt sensitivity: "))
r0 = float(raw_input("R0 [mGal]   : "))
r1 = float(raw_input("R1 [mGal]   : "))
x1 = float(raw_input("X1 [arc sec]: "))

K = math.sqrt( 1 + (87000 * (r0-r1)/(x1*x1)) )

newSens = K * oldSens

print "New tilt Sensitivity: %f"%newSens

