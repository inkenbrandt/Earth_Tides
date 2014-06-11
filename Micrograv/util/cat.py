#!/usr/bin/python
# concatenate files to stdout
# replacement for Unix cat(1) command

import sys

for i in range(1, len(sys.argv)):
  file = open(sys.argv[i], "r");
  while 1:
    line = file.readline();
    if not line: break;
    sys.stdout.write(line)
  file.close();

