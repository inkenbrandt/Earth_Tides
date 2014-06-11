#! /usr/bin/python

# Apply gravity deltas to a plottable file produced by generate_table
#
# Possible uses: adjusting offset of a station/series for the
# 		 zero-value
#		 ajusting relative gravity values for known/modelled
#		 changes, resulting in anomaly values
#		 ....
#
# Deltas are given in a file, the corrected stream is output to stdout;
# redirect to target.
# Errors are given on stderr.
#
# usage: plotDelta.py 'data' 'drift'
# where: 'data' is a plottable (relative) gravity file in the format
# produced by "generate_table" (Y/m/d name relative_grav s.e.)
#        'drift' is a file with date and offset to SUBTRACT from
# relative gravity values; format is yyyy/mm/dd delta(mGal!)
#
# The computed values are output to stdout; redirect to target location

import sys, string;
import grav_util

class PlotDelta:
  def __init__(self, jd, dg):
    self.jd = jd;
    self.dg = dg;

####
### Main routine
##
ewrite = sys.stderr.write;

# check args
if len(sys.argv) < 3:
  ewrite("# usage: %s data drifts\n"%sys.argv[0]);
  ewrite("# where: 'data' is a plottable (relative) gravity file in the format\n");
  ewrite("# produced by 'generate_table' (Y/m/d name relative_grav s.e.)\n");
  ewrite("#        'drift' is a file with date and offset to SUBTRACT from\n");
  ewrite("# relative gravity values; format is yyyy/mm/dd delta(mGal!)\n");
  ewrite("#\n");
  ewrite("# The computed values are output to stdout; redirect to target location\n");
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
    (date, delta) = string.split(line);

    jd = grav_util.str2jd(date, "12:00:00")
    dg = float(delta);
    D.append(PlotDelta(jd, dg));

except:
  ewrite("No drift file.\n");

if len(D) < 1:
  ewrite("No deltas to apply. Why are you running me?\n");

# process data file
file = open(sys.argv[1])
lines = file.readlines()
file.close()

cnt = 0;
for line in lines:
  line = string.strip(line);
  if not line:
    continue;
  if line[0] == "#":
    print line
    continue
  (date, name, g, s) = string.split(line)
  jd = grav_util.str2jd(date, "12:00:00")
  g = float(g)
  for i in range(len(D)):
    if D[i].jd < jd:
      g = g - D[i].dg;
      cnt = cnt + 1;
  sys.stdout.write("%10s %25s %10.3f %10s\n"%(date, name, g, s))
if cnt > 0:
  sys.stdout.write("### %d DATA MODIFIED BY plotDelta.py!\n"%(cnt));
  sys.stdout.write("### cmd-line: %s\n"%(sys.argv))
