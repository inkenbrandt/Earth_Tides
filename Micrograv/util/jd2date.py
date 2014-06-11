#! /usr/bin/python
# convert Absolute Julian Day to date string

import grav_util
import sys, string

if len(sys.argv) < 4:
  print "usage: %s <infile> <outfile> column"%sys.argv[0]
  sys.exit(0)

date_col = int(sys.argv[3]) - 1

infile = open(sys.argv[1], "rt")
outfile = open(sys.argv[2], "wt")

while 1:
  line = infile.readline()
  if not line: break

  cols = string.split(line)
  (year, month, day, hour, minute, second) = grav_util.un_jday(float(cols[date_col]))
  for i in range(date_col):
    outfile.write("%s "%cols[i])
  outfile.write("%02d/%02d/%04d %02d:%02d:%02d "%(month,day,year, hour,minute,
    second))
  for i in range(date_col+1, len(cols)):
    outfile.write("%s "%cols[i])
  outfile.write("\n")
infile.close()
outfile.close()
