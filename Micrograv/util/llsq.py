#! /usr/bin/python
# compute linear least-squares fit to y=ax+b

import string, sys

Print_intercept = 0

# Parse cmd-line
if len(sys.argv) < 4:
  print "usage: %s <infile> x-col y-col [-i]" % sys.argv[0]
  sys.exit()

infile = sys.argv[1]
x_col = int(sys.argv[2])
y_col = int(sys.argv[3])

for i in range(4, len(sys.argv)):
  if sys.argv[i] == "-i":
    Print_intercept = 1

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

# Create data vectors
x = []; y = []
npts = 0
for line in lines:
  line = string.strip(line);

  if not line: continue;
  if line[0] == "#": continue;

  cols = string.split(line)
  x.append(float(cols[x_col]))
  y.append(float(cols[y_col]))
  npts = npts+1

# Compute coefficients
Sxt = Sx = St = Sx2 = 0.0
for i in range(npts):
  Sxt = Sxt + x[i]*y[i]
  Sx = Sx + x[i]
  St = St + y[i]
  Sx2 = Sx2 + x[i]**2

a = (npts*Sxt - Sx*St) / (npts*Sx2 - Sx**2)
b = (St*Sx2 - Sx*Sxt)/(npts*Sx2 - Sx**2)

# Print slope [and intercept]
sys.stdout.write("%f"%a)
if Print_intercept:
  sys.stdout.write(" %f"%b)
sys.stdout.write("\n")

