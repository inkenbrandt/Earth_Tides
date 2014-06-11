#!/usr/bin/python

# create a table from the reformatted output files

import sys, string
from tableWriter import *

#####
### MAIN
#####

if len(sys.argv) < 2:
  print "usage: %s [options] <file>"%sys.argv[0]
  print "options:"
  print "-r	relative values for rows 2+"
  sys.exit(0);

RelativeTable = 0
for i in sys.argv:
  if i == "-r":
    RelativeTable = 1

file = open(sys.argv[-1], "rt")
lines = file.readlines()
file.close()

TABLE={}
for line in lines:
  # parse a line
  fields = string.split(line)
  date = fields[0]
  name = fields[1]
  grav = float(fields[2])
  sigma = float(fields[3])

  if not TABLE.has_key(date):
    # new date
    TABLE[date] = {}

  if not TABLE[date].has_key(name):
    # new station
    TABLE[date][name] = []

  TABLE[date][name].append("%5d %2d"%(grav*1000, sigma*1000))

# write the table
NAMES = {}
dates = TABLE.keys()
for i in dates:
  keys = TABLE[i].keys()
  for j in keys:
    if not NAMES.has_key(j):
      NAMES[j] = 1

dates.sort()
name = NAMES.keys()
name.sort()

# compute maximum column_width
column_width = 1
for j in name:
  if len(j) > column_width:
    column_width = len(j)

for i in dates:
  for j in name:
    if TABLE[i].has_key(j):
      for k in range(len(TABLE[i][j])):
	if len(TABLE[i][j][k]) > column_width:
	  column_width = len(TABLE[i][j][k])

column_width = column_width + 1
if column_width < 11:
  # date fields need 11 chars
  column_width = 11

# header
writer = tableWriter(column_width, 0, " | ")

writer.writeHeader("Relative Gravity Readings\n(uGal)")

writer.writeColumn("DATE")
writer.writeRow(name)
writer.newRow()
strings = ["-"*len(dates[0])]
for j in name:
  strings.append("-"*column_width)
writer.writeRow(strings)
writer.newRow()

campaign = 0
gref = []
for i in dates:
  strings = [i]
  max_n = 1
  n = 0
  while n < max_n:
    if n > 0:
      strings.append("...")
    column=0
    for j in name:
      if TABLE[i].has_key(j):
	if n < len(TABLE[i][j]):
	  fields = string.split(TABLE[i][j][n]);
	  grav = int(fields[0])
	  sigma = int(fields[1])
	  if campaign == 0:
	    if RelativeTable:
	      gref.append(grav);
	    else:
	      gref.append(0.0);
	  else:
	    if column >= len(gref): # new station added
	      if RelativeTable:
		gref.append(grav);
	      else:
		gref.append(0.0);
	    else:
	      grav = grav-gref[column]
	  strings.append("%5d %2d"%(grav, sigma))
	else:
	  strings.append(" "*column_width)
	if len(TABLE[i][j]) > max_n:
	  max_n = len(TABLE[i][j])
      else:
	strings.append(" "*column_width)
	if RelativeTable:
	  if campaign == 0:
	    gref.append(0.0)
      column = column+1
    writer.writeRow(strings)
    writer.newRow()
    strings = []
    n = n+1
  campaign = campaign+1

writer.writeTable()
print "Total # of campaigns: %d"%(campaign)
