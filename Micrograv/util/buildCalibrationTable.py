#!/usr/bin/python

### Build a calibration table from reading, factor values for a
### L&R meter, using the supplied calibration table.

### Note that the L&R table rounds to 0.01 mGal, which is too coarse
### for precision work with an Aliod-equipped meter, so we recompute
### w/rounding to 0.001 mGal from interval factors.....

### enter counter, interval values here
counter = range(0, 7100, 100)
# Factor data taken from Calibration Table for G-1119
factor_base = 1.02
divisor = 1e5	# actual interval factor is (factors[i]/divisor)+factor_base
factors = [519,
	   511,504,498,493,489,486,484,483,483,484,
	   485,488,491,494,499,504,509,516,522,529,
	   537,545,553,562,571,580,590,599,609,619,
	   629,638,648,658,667,677,686,695,704,712,
	   720,728,735,742,748,754,759,764,767,770,
	   773,774,775,774,773,771,768,764,758,752,
	   744,735,725,713,700,686,670,653,634]

grav = [0]
for i in range(1, len(factors)+1):
  F = factors[i-1]/divisor + factor_base
  grav.append(grav[i-1] + (counter[i] - counter[i-1])*F)

for i in range(0,len(grav)):
  print "%4d\t%8.3f"%(counter[i], grav[i])
