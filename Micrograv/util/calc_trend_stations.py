#!/usr/bin/python

## Compute a gnuplot-compatible data file to plot
## gravity data on a linear trend.

## Uses the output of "reduce.py" - that is, the output
## file.  We actually use the raw gravity values, compute the
## difference, and plot half that in the first station, the other
## half in the 2nd station.
##
## Choose the midpoint of the difference to be on the linear trend at
## midway between station times.

import grav_util
import string, sys

class station:
  def __init__(self, name, date, time, grav, sigma):
    self.name = name;
    self.jd = grav_util.str2jd(date, time);
    self.grav = float(grav);
    self.sigma = float(sigma);

if len(sys.argv) < 6:
  print "usage: %s <infile> <drift rate> <start_date> <start_time> <start_g>"%sys.argv[0]
  sys.exit(0);

infile = sys.argv[1];
drift_rate = float(sys.argv[2]);
start_date = sys.argv[3];
start_time = sys.argv[4];
start_grav = float(sys.argv[5]);

start = grav_util.str2jd2(start_date, start_time);

file = open(infile, "rt");
lines = file.readlines();
file.close();

stations = {};

for line in lines:
  line = string.strip(line);
  if not line: continue;
  if line[0] == "#": continue;

  fields = string.split(line);
  if not stations.has_key(fields[0]):
    stations[fields[0]] = [];
  stations[fields[0]].append(station(fields[0], fields[4], fields[5],
    fields[11], fields[12]));

K = stations.keys();
K.sort();
for k in K:
  if len(stations[k]) > 1:
    for i in range(len(stations[k])-1):
      time = (stations[k][i+1].jd + stations[k][i].jd)/2.0
      G = (stations[k][i+1].grav + stations[k][i].grav) / 2.0
      g = start_grav + drift_rate*(time - start);
      g1 = g + (stations[k][i].grav - G);
      g2 = g + (stations[k][i+1].grav - G);
      t1 = stations[k][i].jd
      t2 = stations[k][i+1].jd
      s1 = stations[k][i].sigma
      s2 = stations[k][i+1].sigma
      print "%s %.3f %.3f %s"%(grav_util.datestr2(t1), g1, s1, k)
      print "%s %.3f %.3f %s"%(grav_util.datestr2(t2), g2, s2, k)
      print "\n"
