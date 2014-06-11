#!/usr/bin/python

# prints all files that match */*.out
# equivalent to unix "cat */*.out"

import sys, os, stat

def cat():
  # open all directories we can
  topdirs = os.listdir(os.getcwd());
  topdirs.sort()

  for name in topdirs:
    stats = os.stat(name)
    if(stat.S_ISDIR(stats[0])):
      dirs = os.listdir(name)
      for n in dirs:
	if n[-4:] == ".out":
	  file = open("%s/%s"%(name, n), "rt")
	  while 1:
	    line = file.readline()
	    if not line: break
	    sys.stdout.write(line)

if __name__ == "__main__":
  cat()
