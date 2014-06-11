#!/usr/bin/python

# slabToCorrection.py
#
# Convert a gravity plot file, such as from generate_table, to 
# a correction file such as for remove_base_signal.py, where the
# correction is computed from a change in height of a Bouguer slab.
# This can model the gravity effect of groundwater level rise/fall,
# or any gravity change that is based on a height change of an
# "infinite" slab.
#
# The plot file is used to set the dates of the computed correction;
# "signal" (height) values are extracted for each survey date, and the
# Bouguer slab effect computed for the height difference from a
# supplied reference.
#
# usage: slabToCorrection.py signalFile baseFile outputFile P rho hOffset
# where:
# 	signalFile is a file of "date height" data
#	baseFile is a plot file for the base station
#	outputFile is a name for the output result
#	P is the assumed porosity for the Bouguer slab computation
#	rho is the density, in kg/m^3, of the slab computation
#	hOffset is a constant to subtract from the signalFile values to get
#		the height change
#
# HEIGHTS MUST BE IN METERS, DENSITY IN KG/M^3, POROSITY AS A DECIMAL (0,1.0)!

import sys, string;

if len(sys.argv) < 7:
  print "not enough arguments"
  sys.exit(1);

# read the signalFile first to a dict
signal={}
file = open(sys.argv[1], "rt");
lines = file.readlines();
file.close();

for line in lines:
  line = string.strip(line);
  if not line: continue
  if line[0] == "#": continue
  fields = string.split(line);
  if len(fields) < 2: continue
  # break fields[0] into year, month, day to reformat
  (year,month,day) = string.split(fields[0], "/");
  datestr = "%04d/%02d/%02d"%(int(year),int(month),int(day))
  signal[datestr] = float(fields[1]);

# process the base station plot file
PI = 3.141592654; # for Bouguer slab
G = 6.673e-11; # for Bouguer slab
phi = float(sys.argv[4]);
rho = float(sys.argv[5]);
hOffset = float(sys.argv[6]);

file = open(sys.argv[2], "rt");
lines = file.readlines();
file.close();
out = open(sys.argv[3], "wt");

for line in lines:
  line = string.strip(line);
  if not line: continue;
  if line[0] == "#": continue;
  f = string.split(line)
  # break f[0] into year, month, day to reformat
  (year,month,day) = string.split(f[0], "/");
  datestr = "%04d/%02d/%02d"%(int(year),int(month),int(day))

  if not signal.has_key(datestr):
    print "Base Station measurement without signal value!"
    print "Date: %s"%datestr
    sys.exit(1);

  # dh
  dh = signal[datestr] - hOffset
  # dg
  dg = 2*PI*rho*G*dh*phi*1e5; # convert to mGal

  # output to file
  out.write("%s BCORR %.3f 0.000\n"%(f[0], dg));

# Done!
out.close();
