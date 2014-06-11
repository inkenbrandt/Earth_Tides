# Parse output of reduce.py, and average stations with same names

import string, sys
import grav_util

class Station:
  def __init__(self, name):
    self.name = name
    self.__g = 0.0
    self.__s = 0.0
    self.__nr = 0
    self.__jd = 0.0

  def add_read(self, g, s, jd):
    self.__g = self.__g + (g/s**2)
    self.__s = self.__s + (1/s**2)
    self.__jd = self.__jd + jd
    self.__nr = self.__nr + 1

  def average(self):
    return (float(self.__g / self.__s), float(self.__s**-0.5), float(self.__jd / self.__nr))

def main():
  # filename is argv[1]
  if len(sys.argv) < 2:
    print "usage: %s file\n"%sys.argv[0]
    sys.exit(0)

  file = open(sys.argv[1], "rt")

  # read file and create dictionary
  stations = {}

  while 1:
    line = file.readline()
    if not line: break
    if line[0] == "#":
      # comment, continue
      continue
    if line[0] == "\n":
      # blank line
      continue

    # break apart line
    fields = string.split(line)
    #  0    1 2 3  4    5    6   7  8  9    10      11  12
    # name ID G S Date Time Lon Lat dZ dZ_c Drift_c R_G R_S
    if stations.has_key(fields[0]):
      # add station
      stations[fields[0]].add_read(float(fields[2]), float(fields[3]),
	grav_util.str2jd(fields[4], fields[5]))
    else:
      stations[fields[0]] = Station(fields[0])
      stations[fields[0]].add_read(float(fields[2]), float(fields[3]),
	grav_util.str2jd(fields[4], fields[5]))

  file.close()
  # output averages
  k = stations.keys()
  k.sort()
  for i in k:
    (G, S, JD) = stations[i].average()
    print "%20s %12.3f %12.3f %s"%(i, G, S, grav_util.datestr(JD))

# RUN
main()
