#!/usr/bin/python

import sys, string

def usage():
  print "usage: %s <file> <file>"

def main():
  if len(sys.argv) < 3:
    usage();
    sys.exit(1);

  A={}; B={};
  file = open(sys.argv[1], "rt")
  lines= file.readlines()
  file.close()
  for line in lines:
    line=string.strip(line)
    if not line: continue
    if line[0]=="#": continue
    f=string.split(line);
    A[f[0]] = f[1:]
  file = open(sys.argv[2], "rt")
  lines= file.readlines()
  file.close()
  for line in lines:
    line=string.strip(line)
    if not line: continue
    if line[0]=="#": continue
    f=string.split(line);
    if A.has_key(f[0]):
      pass
      print "%25s %10.3f %6.3f %s"%(f[0],
	float(f[1])-float(A[f[0]][0]),
	float(f[2]), f[3])

main()
