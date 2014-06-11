#! /usr/bin/python
# Compute the average signal from a set of stations over time.
# Assume input files are in the format of "date SID G S" such as is used by
# the table generation programs from reduce.py output files.

# Final data format is "Date SID  dG  S"; a start date for relative
# date computations is chosen by the user.

import sys, string
from math import sqrt
from grav_util import *

class Reading:
  def __init__(self, G, S, ID):
    self.G = float(G)
    self.S = float(S)
    self.ID = ID

def usage():
  print "usage:";
  print "%s StartDate InputFileName -w"%sys.argv[0];
  print "where StartDate is in the format YYYY/MM/DD";
  print "      InputFileName is the name of the input data file, in the";
  print "      format of 'date SID G S' as from the input files to the";
  print "      table generation scripts.";
  print "      -w specifies an UNWEIGHTED average";

def main():
  if len(sys.argv) < 3:
    usage();
    sys.exit();

  startDateString = sys.argv[1];
  inputFileName = sys.argv[2];

  startJD = str2jd(startDateString, "12:00:00")

  file = open(inputFileName, "rt");
  lines = file.readlines();
  file.close();

  averageFlag=0;	# weighted average
  if len(sys.argv)>3:
    if sys.argv[3] == "-w":
      averageFlag = 1;	# unweighted average

  # create a dictionary of the data, keyed on date
  rawdata = {}
  stations = {}
  names = {}

  for line in lines:
    line = string.strip(line);
    if not line: continue;
    fields = string.split(line);
    # line is: DateStr SID dG S
    jd = str2jd(fields[0], "12:00:00")
    jd = jd - startJD;
    if not rawdata.has_key(jd):
      rawdata[jd] = []
    rawdata[jd].append(Reading(float(fields[2]), float(fields[3]), fields[1]))

  for d in rawdata.keys():
    stations[d] = {}
    for i in range(len(rawdata[d])):
      ID = rawdata[d][i].ID
      if not stations[d].has_key(ID):
	stations[d][ID] = 1
      if not names.has_key(ID):
	names[ID] = 1

  # average same stations for each date
  data = {}
  for d in rawdata.keys():
    data[d] = []
    for s in names.keys():
      g = []; dg = [];
      for i in range(len(rawdata[d])):
	if rawdata[d][i].ID == s:
	  g.append(rawdata[d][i].G)
	  dg.append(rawdata[d][i].S)
      (G, S) = weightedAverage(g, dg)
      if S != 0.0:
	data[d].append(Reading(G, S, s))

  # now have dict of (dG, S) by julian date
  # So, now test that each station has an entry for each date
  # if it doesn't, interpolate an entry
  dates = data.keys()
  dates.sort(num_sort)
  for d in dates:
    for ids in names.keys():
      if not stations[d].has_key(ids):
	stations[d][ids] = 1
	(G, S) = interpolate(d, data, ids, stations)
        data[d].append(Reading(G, S, s))

  # now, for each date, we compute the average dG and store
  signal = {}
  error = {}
  for d in dates:
    g = []; s = []
    for i in range(len(data[d])):
      g.append(data[d][i].G)
      s.append(data[d][i].S)
    if averageFlag:
      (G, S) = sampleAverage(g)
    else:
      (G, S) = weightedAverage(g, s)
    signal[d] = G
    error[d] = S

  # spit it out in a nice format
  for d in dates:
    D = datestr(d+startJD)
    print "%s\tASIG\t%.3f\t%.3f"%(D[0:10], signal[d], error[d])


def interpolate(jd, data, ID, stations):
  # interpolate the value for station ID and date jd using nearest neighbors
  # first, need to find nearest neighbors
  dates = data.keys()
  dates.sort(num_sort)
  d1 = min(dates); d2 = max(dates);
  for d in dates:
    if d<jd and d>d1 and stations[d].has_key(ID):
      d1 = d;
    elif d>jd and d<d2 and stations[d].has_key(ID):
      d2 = d;

  # now, we get the readings to interpolate
  g1 = 0.0; s1 = 0.0; g2 = 0.0; s2 = 0.0
  for i in range(len(data[d1])):
    if data[d1][i].ID == ID:
      g1 = data[d1][i].G
      s1 = data[d1][i].S
  for i in range(len(data[d2])):
    if data[d2][i].ID == ID:
      g2 = data[d2][i].G
      s2 = data[d2][i].S

  # interpolate the values
  m = (g2-g1)/(d2-d1)
  G = m * (jd - d1) + g1
  S = sqrt(s2*s2 + 2*s1*s1)
  return (G, S)
    

if __name__ == "__main__":
  main()
