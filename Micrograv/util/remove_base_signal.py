#! /usr/bin/python
# Remove the average base station signal from the gravity readings.
# Requires the output file from get_ave_signal.py, and the files used
# in generate_table.

# Should be called from generate_table

import sys, string
from math import sqrt
from grav_util import *

class Reading:
  def __init__(self, G, S, ID):
    self.G = float(G)
    self.S = float(S)
    self.ID = ID

def main():
  global min_JD, max_JD;
  if len(sys.argv) < 3:
    sys.exit();

  aveFileName = sys.argv[1];
  dataFileName = sys.argv[2];

  file = open(aveFileName, "rt");
  lines = file.readlines();
  file.close();

  # create a dictionary of the average signal, keyed on date
  average = {}

  for line in lines:
    line = string.strip(line);
    if not line: continue;
    fields = string.split(line);
    # line is: DateStr SID dG S
    jd = str2jd(fields[0], "12:00:00")
    jd = jd;
    average[jd] = float(fields[2]);

  # find max/min dates
  k = average.keys();
  min_JD = min(k);
  max_JD = max(k);

  # now read data file.
  # for each entry, compute the average signal to remove - i.e.
  # interpolate the value from nearest neighbors; simple linear scheme
  file = open(dataFileName, "rt");
  lines = file.readlines();
  file.close();

  for line in lines:
    line = string.strip(line);
    if not line: continue;
    fields = string.split(line);
    # line format is: DateStr SID G S
    jd = str2jd(fields[0], "12:00:00")
    # compute the correction
    dG = interpolate(jd, average);
    G = float(fields[2]) - dG;

    # spit out the line
    print "%s %12s %.3f %s"%(fields[0], fields[1], G, fields[3]);

  # done



def interpolate(jd, signal):
  global min_JD, max_JD;
  # Find nearest bracketing date entries, use linear interpolation

  # test that the date is within the bounds of the signal data
  if jd <= min_JD:
    return signal[min_JD];
  if jd >= max_JD:
    return signal[max_JD];

  lb = min_JD
  ub = max_JD

  # within bounds, so we can interpolate
  for k in signal.keys():
    if k<=jd and k>lb:
      lb = k;
    if k>jd and k<ub:
      ub = k;

  # get values for interpolation
  lbVal = signal[lb];
  ubVal = signal[ub];

  # linear interpolation
  m = (ubVal - lbVal) / (ub - lb);
  dG = lbVal + m * (jd - lb);
  return dG;
  # end interpolate()


if __name__ == "__main__":
  main()
