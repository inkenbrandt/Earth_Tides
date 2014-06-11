# deltag - take concatenated output files from reduce, extract a
# particular station, and compute the change in gravity from first value,
# with time stamping in output

import sys, string, time

from grav_data import Station

#####################
##### Main Code #####
#####################
# get cmd-line args
if len(sys.argv) < 2:
  sys.stderr.write("usage: %s <infile>\n"%sys.argv[0])
  sys.exit(0)

infile = open(sys.argv[1], "rt")

stations = {}

# parse the file, creating dictionary of stations
date = "Unknown"
while 1:
  line = infile.readline()
  if not line: break
  # parse the line
  if line[0] == '#':
    # comment line, trap for date
    if line[0:16] == '#Reference Date:':
      # date line, so split it
      (a, a, date, b) = string.split(line, None, 3)
      continue
  elif line[0] == '\n':
    # blank line
    continue
  else:
    # data line
    (name, sid, grav, sigma, rest) = string.split(line, None, 4)
    if not stations.has_key(name):
      stations[name] = []
    stations[name].append(Station(name, float(grav), float(sigma), date))

infile.close()

# write output file
keys = stations.keys()
keys.sort()
for i in keys:
  file = open(i, "wt")
  for j in range(len(stations[i])):
    file.write("%s %s %f %f\n"%(stations[i][j].date, stations[i][j].name,
      stations[i][j].gravity, stations[i][j].sigma))
  file.close()

