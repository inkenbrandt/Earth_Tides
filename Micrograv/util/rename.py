#!/usr/bin/python
# rename stations according to the file supplied on command line

import sys, string, re

def doit(namefile, filename):
  file = open(namefile, "rt");
  lines = file.readlines()
  file.close()

  names = {}
  for line in lines:
    fields = string.split(line, None, 1)
    key = string.strip(fields[0])
    val = string.strip(fields[1])
    names[key] = val

  file = open(filename, "rt")
  lines = file.readlines()
  file.close()

  for line in lines:
    for k in names.keys():
      line = re.sub(k, val, line);
    sys.stdout.write(line)

if __name__ == "__main__":
  if len(sys.argv) < 3:
    print "usage: %s namefile inputfile"%sys.argv[0]
    sys.exit();
  doit(sys.argv[1], sys.argv[2])
