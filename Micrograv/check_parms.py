#!/usr/bin/python
# Check station parameter file for common errors

# specifically, we want to make sure that:
# 1. every repeat of a station is truly a repeat (i.e. names are identical)
# 2. every station with identical names is in the repeat list
# 3. All stations have reasonable lat/lon
# 4. All station IDs have a name

import sys, string;

import fileop, grav_util;

def usage():
  print "%s <filename>"%sys.argv[0]

if len(sys.argv) < 2:
  usage();
  sys.exit(0);

for i in range(1,len(sys.argv)):
  parm_file = sys.argv[i]

  print "Checking file %s:"%parm_file
  try:
    parms = fileop.get_sta_parms(parm_file);
    names = fileop.get_sta_names(parm_file);
    repeats = fileop.get_sta_repeats(parm_file);
  except:
    print "unable to read/parse parameter file %s."%parm_file
    continue

  # check lat/lon
  keys = parms.keys()
  keys.sort(grav_util.num_sort)
  for i in keys:
    # latitude
    if parms[i].lat > 90.0 or parms[i].lat < -90.0:
      print "WARNING: Station ID '%s' has suspicious latitude of %f!"%(i, parms[i].lat);
    if parms[i].lon > 180 or parms[i].lon < -180:
      print "WARNING: Station ID '%s' has suspicious longitude of %f!"%(i, parms[i].lat);

  keys = repeats.keys()
  keys.sort(grav_util.num_sort)
  # check repeats
  for i in keys:
    if not names.has_key(i):
      print "ERROR: Station ID '%s' has no name entry!"%i
      break
    Name = names[i];
    for j in range(len(repeats[i])):
      # check that each repeat id has the same name
      if not names.has_key(repeats[i][j]):
	print "ERROR: Station ID '%s' has no name entry!"%repeats[i][j]
	break
      if names[repeats[i][j]] != Name:
	print "WARNING: Station ID '%s' has repeat ('%s') with different name ('%s')!"%(Name, repeats[i][j], names[repeats[i][j]]);

    # check that we have a listing in repeats[i] for each station with the same name
    for j in names.keys():
      if names[j] == Name:
	if j != i:
	  match = 0;
	  for k in range(len(repeats[i])):
	    if repeats[i][k] == j:
	      # we have a match, so OK
	      match = 1
	  if not match:
	    print "WARNING: Station ID '%s' has same name ('%s') as station ID '%s', but is not in repeat list for station!"%(j, names[j], i)
  # all done
  print "Done checking file %s."%parm_file
