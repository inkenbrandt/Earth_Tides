#!/usr/bin/python

##
# Difference 2 files with coordinates in "name x y z" format
# format.
##

import string, sys

def main():
  if len(sys.argv) < 3:
    print "usage: diffCoords.py file1 file2"
    sys.exit(1);

  file = open(sys.argv[1], "rt")
  lines = file.readlines();
  file.close();

  c1 = {}
  for line in lines:
    line = string.strip(line);
    if not line: continue
    if line[0] == "#": continue
    fields = string.split(line);

    c1[fields[0]] = (float(fields[1]), float(fields[2]),
      float(fields[3]));

  file = open(sys.argv[2], "rt")
  lines = file.readlines();
  file.close();

  c2 = {}
  for line in lines:
    line = string.strip(line);
    if not line: continue
    if line[0] == "#": continue
    fields = string.split(line);

    c2[fields[0]] = (float(fields[1]), float(fields[2]),
      float(fields[3]));

  for k in c1.keys():
    if c2.has_key(k):
      print "%15s %12.6f %12.6f %12.6f %12.6f %12.6f %12.6f"%(k,
        c1[k][0], c1[k][1], c1[k][2], c2[k][0] - c1[k][0],
	c2[k][1] - c1[k][1], c2[k][2] - c1[k][2]);

##
# RUN!
##
main()
