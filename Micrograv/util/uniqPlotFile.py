#!/usr/bin/python

# Keep only the entry for a date with the largest s.d.

import sys,string

if len(sys.argv) < 2:
  sys.stderr.write("usage: %s FILE [FILE ...]"%sys.argv[0]);

for index in range(1,len(sys.argv)):
  file=open(sys.argv[index]);
  lines = file.readlines();
  file.close();
  gravVals = {};
  for line in lines:
    line = string.strip(line);
    if not line: continue;
    if line[0] == "#": continue;

    (date, name, grav, sig) = string.split(line);
    grav = float(grav); sig = float(sig);
    if not gravVals.has_key(date):
      gravVals[date] = [grav, sig, name];
    else:
      if gravVals[date][1] < sig:
        gravVals[date][0] = grav;
        gravVals[date][1] = sig;
        gravVals[date][2] = name;
  keys=gravVals.keys();
  keys.sort();
  for k in keys:
    print "%10s\t%5s\t%6.3f\t%6.3f"%(k, gravVals[k][2], gravVals[k][0], gravVals[k][1])

