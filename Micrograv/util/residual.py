#! /usr/bin/python
# Compute average, and remove it from a column

import string, sys

# Parse cmd-line
if len(sys.argv) < 4:
  print "usage: %s <infile> <outfile> col" % sys.argv[0]
  sys.exit()

infile = sys.argv[1]
outfile = sys.argv[2]
y_col = int(sys.argv[3])

y_col = y_col-1

# Open data file for read
try:
  file = open(infile, "rt")
except:
  print "cannot open %s for read. exit to system."%infile
  sys.exit()

# Read the whole file
lines = file.readlines()
file.close()

try:
  ofile = open(outfile, "wt")
except:
  print "cannot open % for write. exit."%outfile
  sys.exit()

# compute average
npts = 0
average = 0
for i in range(len(lines)):
  line = lines[i]

  if line[0] == "\r" or line[0] == "\n" or line[0] == "#":
    continue

  cols = string.split(line)
  y = float(cols[y_col])

  average = average+y
  npts = npts+1

average = average/npts

for i in range(len(lines)):
  line = lines[i]

  if line[0] == "\r" or line[0] == "\n" or line[0] == "#":
    ofile.write(line)
    continue

  cols = string.split(line)
  y = float(cols[y_col])

  y = y-average

  cols[y_col] = "%.3f"%y

  for j in range(len(cols)):
    ofile.write("%s "%cols[j])
  ofile.write("\n")

ofile.close()
