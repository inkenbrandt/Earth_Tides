#! /usr/bin/python
# convert date string to absolute julian date

import grav_util
import sys, string

if len(sys.argv) < 3:
  print "usage: %s mm/dd/yyyy hh:mm:ss"%sys.argv[0]
  sys.exit(0)

datestr = sys.argv[1]
timestr = sys.argv[2]
fields = string.split(datestr, "/")
if int(fields[0]) > 12:
  # month > 12, so we assume we actually have a yyyy/mm/dd format
  datestr = "%s/%s/%s"%(fields[1], fields[2], fields[0])
print grav_util.str2jd2(datestr, timestr)
