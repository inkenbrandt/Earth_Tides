#! /usr/bin/python

# compute relative values of gravity
# assume data file in correct format: "date sid G S"

import sys, string


def calc(filename):
  file = open(filename);
  lines = file.readlines();
  file.close();

  i=0;
  for line in lines:
    fields = string.split(line)
    i = i+1
    if i == 1:
      offset = float(fields[2])
    G = float(fields[2]);
    print "%s\t%s\t%.3f\t%s"%(fields[0], fields[1], G-offset, fields[3])

if __name__ == "__main__":
  if len(sys.argv) < 2:
    sys.exit();
  calc(sys.argv[1]);

