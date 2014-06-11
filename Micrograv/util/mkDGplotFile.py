#!/usr/bin/python

import string, sys

####
## Input files-
##   Position file, in format for make_parm_file
##   Station file, with station ID, dG, sigma in columns
####

def usage():
  print "usage:\n"
  print "  %s positionfile idfile\n"%sys.argv[0]


def main():
  if len(sys.argv) < 3:
    usage()
    sys.exit(0);

  posFileName = sys.argv[1]
  idFileName = sys.argv[2]

  file = open(posFileName, "rt");
  lines = file.readlines();
  file.close();

  stations = {}
  for line in lines:
    line = string.strip(line);
    if not line: continue;
    if line[0] == "#": continue;

    F = string.split(line);
    stations[F[0]] = line;

  file = open(idFileName, "rt")
  lines = file.readlines();
  file.close();

  for line in lines:
    line = string.strip(line);
    if not line: continue
    if line[0] == "#": continue

    F = string.split(line);

    if stations.has_key(F[0]):
      data = reduce(lambda x,y:x+y+" ", F[1:], " ")
      print "%s %s"%(stations[F[0]], data)

main();
