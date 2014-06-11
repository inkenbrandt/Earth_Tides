#!/usr/bin/python

# Break apart a DC file, v7.5

import sys

if len(sys.argv)<2:
  infile = sys.stdin
else:
  infile = open(sys.argv[1], "rt")

lines = infile.readlines()
filename = "UNKNOWN"
station = "UNKNOWN"
anthgt = -1.00
hgttype = "UNKN"; flag = 0
for line in lines:
  line = line.strip()
  if line[0:2] == "72":	# post processing filename
    # write out existing info, prepare for next entry
    if flag:
      sys.stdout.write("%16s %16s %8.4f %s\n"%(filename, station, anthgt, hgttype))
    station = "UNKNOWN"; anthgt = -1.00; hgttype = "UNKN";	# reset
    filename = line[4:len(line)]
    flag = 1;
    continue
  if line[0:2] == "57": # antenna height
    anthgt = float(line[4:20])
    hgttype = "UNKN"
    if line[20] == "1":
      hgttype = "TRUE"
    if line[20] == "2":
      hgttype = "UNCO"
    continue
  if line[0:2] == "66": # GPS position, with point name
    station = line[4:20].strip()

