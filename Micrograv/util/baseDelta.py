#! /usr/bin/python

# Correct a concatenated set of reduce.py output files (stripped of
# comments!) for base station drifts.
#
# Drifts are given in a file, the corrected stream is output to stdout.
# Errors are given on stderr.

import sys, string;
import grav_util

class BaseDelta:
  def __init__(self, jd, dg):
    self.jd = jd;
    self.dg = dg;

####
### Main routine
##
ewrite = sys.stderr.write;

# check args
if len(sys.argv) < 3:
  ewrite("  usage: %s data drifts\n"%sys.argv[0]);
  ewrite("  'data' should be a concatenated set of reduced gravity surveys,\n");
  ewrite("  with comments removed.  'drifts' should be a file with dates and\n");
  ewrite("  offsets; dates are in YYYY/MM/DD HH:MM:SS format, and offsets are\n");
  ewrite("  differences, in mGal, to ADD to the following stations.  All stations\n");
  ewrite("  receive all deltas that are prior in time to their occupation time.\n");
  ewrite("\n");
  ewrite("  Offsets can be any sign, and any size.\n");
  sys.exit(1);

# process delta file
D = [];
try:
  file = open(sys.argv[2])
  lines = file.readlines();
  file.close()

  for line in lines:
    line = string.strip(line);
    if not line:
      continue
    if line[0] == "#":
      continue
    (date, time, delta) = string.split(line);

    jd = grav_util.str2jd(date, time)
    dg = float(delta);
    D.append(BaseDelta(jd, dg));

except:
  ewrite("No drift file.\n");

if len(D) < 1:
  ewrite("No drifts to apply.\n");

# process data file
file = open(sys.argv[1])
lines = file.readlines()
file.close()

cnt = 0;
for line in lines:
  line = string.strip(line);
  if not line:
    continue;
  (sid, snm, g, s, date, time, lon, lat, hgt, dz, dzc, drift, rg, rs) = string.split(line)
  jd = grav_util.str2jd(date, time)
  g = float(g)
  for i in range(len(D)):
    if D[i].jd < jd:
      g = g + D[i].dg;
      cnt = cnt + 1;
  sys.stdout.write("%25s %15s %10.3f %5s %20s %11s %11s %7s %7s %7s %8s %5s\n" %
    (sid, snm, g, s, date+" "+time, lon, lat, dz, dzc, drift, rg, rs))
if cnt > 0:
  sys.stdout.write("### %d DATA MODIFIED BY baseDelta.py!\n"%(cnt));
  sys.stdout.write("### cmd-line: %s\n"%(sys.argv))
