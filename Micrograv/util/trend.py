#! /usr/bin/python
# Remove a linear trend from a data set

import string, sys

# Parse cmd-line
if len(sys.argv) < 6:
  print "usage: %s <infile> <outfile> x-col y-col slope" % sys.argv[0]
  sys.exit()

infile = sys.argv[1]
outfile = sys.argv[2]
x_col = int(sys.argv[3])
y_col = int(sys.argv[4])
slope = float(sys.argv[5])
remove_intercept = 0;
if len(sys.argv) > 6:
  intercept = float(sys.argv[6])
  remove_intercept = 1

x_col = x_col-1
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

# Remove trend
npts = 0
for i in range(len(lines)):
  line = lines[i]

  if line[0] == "\r" or line[0] == "\n" or line[0] == "#":
    ofile.write(line)
    continue

  cols = string.split(line)
  x = float(cols[x_col])
  y = float(cols[y_col])

  if npts == 0:
    x0 = x

  y = y-(slope*(x-x0))
  if remove_intercept:
    y = y - intercept

  cols[y_col] = "%.3f"%y
  npts = npts+1

  for j in range(len(cols)):
    ofile.write("%s "%cols[j])
  ofile.write("\n")

ofile.close()
