#!/usr/bin/python

# Add a computed inner zone terrain correction to a pfact file, keeping
# format

import sys, string

def usage():
  sys.stderr.write("usage: %s pfact_file iztc_file\n"%sys.argv[0])
  sys.stderr.write("result is spewed to stdout.  Redirect if needed\n");
  sys.exit(1)


if len(sys.argv)<3:
  usage()

pfact_file = open(sys.argv[1], "rt")
iztc_file = open(sys.argv[2], "rt")

lines = iztc_file.readlines()
iztc_file.close()

iztc = {}
for line in lines:
  line = line.strip()
  if not line: continue;
  if line[0] == "#": continue;
  fields = line.split()
  iztc[fields[0]] = float(fields[1])

for line in pfact_file:
  line = line.strip()
  if not line: continue;
  if line[0] == "#": continue;

  fields = line.split()

  print "%-8s%4s%7s%6s%5s%7s%6s%2s%8s%5s%11s%6s%6.2f%11s%11s"%(fields[0],
    fields[1], fields[2], fields[3], fields[4], fields[5], fields[6], fields[7], fields[8], fields[9],
    fields[10], fields[11], iztc[fields[0]], fields[13], fields[14])

pfact_file.close()
