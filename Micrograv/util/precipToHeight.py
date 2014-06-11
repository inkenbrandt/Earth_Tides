#!/usr/bin/python

# Convert a set of date/precip values to a file of date/height
# values.  The height is computed by taking all values for a previous
# interval and summing.  This is essentially a backwards-looking
# accumulator in a sliding window.
#
# usage: precipToHeight.py precipFile heightFile interval
# where:
# 	precipFile is a file of "date(yyyy/mm/dd) precip" pairs, assumed daily values
#	heightFile is the output file of "yyyy/mm/dd totalPrecip"
#	interval is the length of time, in entries, for the backwards-looking
#		 accumulator
#
# PRECIP ASSUMED TO BE IN METERS

import sys, string;

if len(sys.argv) < 4:
  print "not enough arguments"
  sys.exit(1);

window = int(sys.argv[3]);

# read the data file to an array
file = open(sys.argv[1], "rt");
lines = file.readlines();
file.close();

dates = [];
precip = [];

for line in lines:
  line = string.strip(line);
  if not line: continue;
  if line[0] == "#": continue;
  f = string.split(line);
  dates.append(f[0]);
  precip.append(float(f[1]));

out = open(sys.argv[2], "wt");
# nested for loops to do the accumulating
for i in range(len(dates)):
  k=i-window;
  if k < 0: k=0
  s = 0;
  for j in range(k, i+1):
    s += precip[j];
  out.write("%s %f\n"%(dates[i], s));

# done
out.close();
