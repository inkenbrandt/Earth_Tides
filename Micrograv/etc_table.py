#!/usr/bin/python 
# etc_table - Print table of Earth Tide Corrections
#
# given a lat, lon, z, GMT offset and day, compute 24hrs of
# ETCs.

import sys, string
#from math import *
import tamura
import jd

## Time step for computing ETC
deltaTau = 3.47222222e-3;	# 5 min in days

### Main
if len(sys.argv) < 6:
  sys.stderr.write("usage: %s yyyy-mm-dd lat lon elevation GMT_offset\n"%sys.argv[0])
  sys.stderr.write("lat & lon are positive N & E, elevation in meters ASL, GMT offset positive for east of GMT\n")
  sys.exit(1);

datestr = string.replace(sys.argv[1], "-", "/")
start = jd.str2jd(datestr, "00:00:00");	# start at midnight

lat = float(sys.argv[2]);
lon = float(sys.argv[3]);
ele = float(sys.argv[4]);
GMT = float(sys.argv[5]);

N = int(1/deltaTau)+1	# number of steps for 1 day + 5 min
print "ETC (mGal) for %s at %.6f N %.6f E %.3f m ASL, GMT off: %.2f"%(datestr, lat, lon, ele, GMT)
for i in range(N):
  t = start + (i*deltaTau)
  (year, month, day, hour, minute, second) = jd.un_jday(t)

  C = tamura.tide(year, month, day, hour, minute, second, lon, lat, ele, 0.0, GMT)
  print "%2d:%02d:%02d\t%.4f"%(hour, minute, second, C/1000.0)

