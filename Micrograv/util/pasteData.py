#!/usr/bin/python
#
# Paste 2 data files together, keyed by station name
# Assumes the first column of every file is the station name!
# Only pastes stations with entries in both files!
#
import string, sys

def usage():
  print "usage: %s file1 file2"%(sys.argv[0])
  print "file1 and file2 must have Station ID as first column!"

def main():
  if len(sys.argv) < 3:
    usage()
    sys.exit(1);

  S={}

  file=open(sys.argv[1], "rt")
  lines=file.readlines();
  file.close();
  for line in lines:
    line = string.strip(line);
    if not line: continue;
    if line[0] == "#": continue;
    F=string.split(line)
    S[F[0]] = reduce(lambda x,y:x+y+" ", F[1:], " ");

  file=open(sys.argv[2], "rt")
  lines=file.readlines();
  file.close();
  for line in lines:
    line = string.strip(line);
    if not line: continue;
    if line[0] == "#": continue;
    F=string.split(line)
    if S.has_key(F[0]):
      print "%s %s %s"%(F[0],S[F[0]], reduce(lambda x,y:x+y+" ", F[1:], " "))


## RUN!
main()
