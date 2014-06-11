#!/usr/bin/python
#
## averageFirstReadings.py - Average the first N readings, where N
## is set by a date.  All values prior (not equal!) to the specified
## date are averaged.
#
# usage: averageFirstReadings.py yyyy mm dd filename
#
# This expects the file named by 'filename' to be in the format output
# by 'generate_table': yyyy/mm/dd name g s.e.
#
# The resulting average is printed to stdout; errors spewed to stderr

import sys, string, grav_util

ewrite = sys.stderr.write;

# check args
if len(sys.argv) < 5:
  ewrite("# usage: averageFirstReadings.py yyyy mm dd filename [filename ...]\n");
  ewrite("#\n");
  ewrite("# This expects the file named by 'filename' to be in the format output\n");
  ewrite("# by 'generate_table': yyyy/mm/dd name g s.e.\n");
  ewrite("#\n");
  ewrite("# The resulting average is printed to stdout; errors spewed to stderr\n");
  ewrite("# ALL files are computed into a single average!\n");
  sys.exit(1);

year = sys.argv[1];
mm = sys.argv[2];
dd = sys.argv[3];

sday = grav_util.str2jd("%s/%s/%s"%(year, mm, dd), "12:00:00");
S = 0.0;
N = 0.0;

# process files
for i in range(4, len(sys.argv)):
  file = open(sys.argv[i])
  lines = file.readlines()
  file.close()

  for line in lines:
    line = string.strip(line);
    if not line:
      continue;
    (date, name, g, s) = string.split(line)
    jd = grav_util.str2jd(date, "12:00:00")
    g = float(g)
    if jd < sday:
      S += g;
      N += 1;
# print average
if N == 0:
  sys.stdout.write("0.000\n");
  ewrite("averageFirstReadings.py: ERROR - N = 0, no readings before date %s/%s/%s\n"%(year, mm, dd));
else:
  sys.stdout.write("%10.3f\n"%(S/N));
