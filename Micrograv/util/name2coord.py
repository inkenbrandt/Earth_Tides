#!/usr/bin/python

####
### Convert a file with 3 columns: name dg s.d. to a file with
### 4 columns: x y dg s.d.
###
### Normally used with UTM coordinates (but could be lat/lon) and
### the output from gravity reduction (after massaging with awk/perl).
###
### Format for coordinate file is:
###    name x y
####

import sys, string

if len(sys.argv) < 3:
  sys.stderr.write("usage: %s dataFile coordFile\n"%sys.argv[0]);
  sys.exit(1);

file = open(sys.argv[2], "rt");
lines = file.readlines();
file.close();

C = {}
for line in lines:
  line = string.strip(line);
  if not line:
    continue;
  f = string.split(line);

  C[f[0]] = (f[1], f[2]);

file = open(sys.argv[1], "rt");
lines = file.readlines();
file.close();

for line in lines:
  line = string.strip(line)
  if not line:
    continue;
  f = string.split(line);
  if not C.has_key(f[0]):
    sys.stderr.write("ERROR: No coordinates for station id %s\n"%f[0])
    continue
  print "%s %s %s %s"%(C[f[0]][0], C[f[0]][1], f[1], f[2])
