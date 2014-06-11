#!/usr/bin/python

##
# Add a x,y,z offset to coordinates in a file.
#
# Note: entries with no offsets will have an average added.
#
# Files in simple format: name x y z
##

import string, sys

def main():
  if len(sys.argv) < 3:
    print "usage: offsetCoords.py coords offsets"
    sys.exit(1);

  file = open(sys.argv[2], "rt")
  lines = file.readlines();
  file.close();

  offsets = {}
  for line in lines:
    line = string.strip(line);
    if not line: continue
    if line[0] == "#": continue
    fields = string.split(line);

    offsets[fields[0]] = (float(fields[1]), float(fields[2]),
      float(fields[3]));

  file = open(sys.argv[1], "rt")
  lines = file.readlines();
  file.close();

  n = 0; x=0; y=0; z=0;
  for k in offsets.keys():
    x += offsets[k][0];
    y += offsets[k][1];
    z += offsets[k][2];
    n += 1;
  x /= n;
  y /= n;
  z /= n;

  coords = {}
  for line in lines:
    line = string.strip(line);
    if not line: continue
    if line[0] == "#": continue
    fields = string.split(line);

    coords[fields[0]] = (float(fields[1]), float(fields[2]),
      float(fields[3]));

  for k in coords.keys():
    if offsets.has_key(k):
      print "%-15s %12.6f %12.6f %12.6f"%(k,
	coords[k][0]+offsets[k][0], coords[k][1]+offsets[k][1],
	coords[k][2]+offsets[k][2])
    else:
      print "%-15s %12.6f %12.6f %12.6f"%(k,
	coords[k][0]+x, coords[k][1]+y, coords[k][2]+z)

##
# RUN!
##
main()
