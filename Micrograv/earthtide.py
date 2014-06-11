#! /opt/bin/python
# etide - Earth Tide Corrections
# use the best formulas we can, assuming no ETC from the meter!
# this turns out to be Tamura's correction scheme

# for speed, we would like to use the C version of Tamura's
# computation, since that runs orders faster than Python
import sys, string
import grav_util
import etc

# main routine
def main():
  if len(sys.argv)<6:
    print "usage: earthtide.py <file> <lat> <lon> <ele> <GMT off>"
    sys.exit(0)

  file = open(sys.argv[1], "rt")
  lines = file.readlines()
  file.close()

  lat = float(sys.argv[2])
  lon = float(sys.argv[3])
  ele = float(sys.argv[4])
  gmt = float(sys.argv[5])

  # parse the data file
  for line in lines:
    line = string.strip(line)
    if not line:
      print 
      continue
    fields = string.split(line, None, 1)
    (M, D, Y) = string.split(fields[0], '/',2)
    Y = int(Y); M = int(M); D = int(D)
    if Y < 70:
      Y = Y+100
    Y = Y+1900
    (h, m) = string.split(fields[1], ':', 1)
    h = int(h); m = int(m)
    jd = grav_util.calc_jday(Y, M, D, h, m, 0)
    C = correction(jd, lat, lon, ele, gmt)
    print "%-20s %10.3f"%(line, C)

def correction(date, lat, lon, ele, gmt):
  # compute Tamura ETC
  (year, month, day, hour, minute, second)=grav_util.un_jday(date)

  C = etc.tide(year, month, day, hour, minute, second,
    lon, lat, ele, 0.0, gmt)

  # Tamura's routine yields results in microgal!
  return C/1000.0



main()
