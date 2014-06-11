#!/usr/bin/python
# compute tilt zero error from data as specified in manual

print "Tilt Zero Error Calculator"
print "See pg 6-4 in manual"
print "X1/X2 refer to tilt measurements, in arc sec, for either axis"
print "R1/R2 refer to gravimeter readings, in mGal"
x1 = float(raw_input("X1 [arc sec]: "))
r1 = float(raw_input("R1 [mGal]   : "))
x2 = float(raw_input("X2 [arc sec]: "))
r2 = float(raw_input("R2 [mGal]   : "))

err = (r2-r1)/(x1-x2) * 43386

print "Zero error = %f arc sec"%err
print "Adjust via the fine[coarse] adjustment pot. under the face plate."
print "See pg 6-6 in manual"
