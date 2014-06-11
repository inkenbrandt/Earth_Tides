#!/usr/bin/python

# check a raw data file for errors
# if any, try to give line number of error

import sys

# custom modules
import cg3file

#Parse command-line args
if len(sys.argv) < 2:
  print "usage: %s <file>"%sys.argv[0]
  sys.exit(0)
for i in range(1,len(sys.argv)):
  raw_file = sys.argv[i]

  # try to read the file, and let the fileop.py handlers take care of things
  print "Processing file %s..."%raw_file
  try:
    raw_data = cg3file.get_cg3_data(raw_file)
  except:
    print "Error encountered...aborting."
  else:
    print "%d data records\n"%(len(raw_data))
