#! /usr/bin/python

# command line based data extraction from Aliod raw data
# Uses raw output of Gravlog, parses it, and outputs a text file for
# plotting
import sys, string
import time

import aliodfile
import grav_util
from grav_data import *
import tamura
earth_tide=tamura.tide

class Fields:
  def __init__(self):
    self.rel_date = 0
    self.abs_date = 0
    self.time_str = 0
    self.station_id = 0
    self.gravity = 0
    self.tilt_x = 0
    self.tilt_y = 0
    self.temp = 0
    self.tetc = 0
    self.lat = 0
    self.lon = 0
    self.GMT = 0

#
# BEGIN UTILITY FUNCTIONS
#
def cmd_write_header(file, fields):
  file.write("#")
  if fields.rel_date == 1:
    file.write(" __RELDAY__")
  if fields.abs_date == 1:
    file.write(" _____JULIAN DATE____")
  if fields.time_str == 1:
    file.write(" _____DATE/TIME_____")
  if fields.station_id == 1:
    file.write(" ___STATION ID STRING_____")
  if fields.gravity == 1:
    file.write(" _GRAVITY")
  if fields.tilt_x == 1:
    file.write(" TILT_X")
  if fields.tilt_y == 1:
    file.write(" TILT_Y")
  if fields.temp == 1:
    file.write(" _TEMP_")
  if fields.tetc == 1:
    file.write(" T_ETC_")
  if fields.lat == 1:
    file.write(" LATITUD")
  if fields.lon == 1:
    file.write(" LONGITUD")
  if fields.GMT == 1:
    file.write("  LT-GMT ")
  file.write("\n")


def cmd_tide_error(i, jul_day, year, month, day, hour, minute, second, lat, lon, elevation, GMT_Diff):
  error_msg = "\tError in input parameters to tide correction routine!\n"
  error_msg = error_msg + "\tData point #%d\n" % i
  error_msg = error_msg + "\tJulian Date: %f\n" % jul_day
  error_msg = error_msg + "\tParameters are- date/time %f/%f/%f %d:%d:%f\n" % (year,
	  month, day, hour, minute, second)
  error_msg = error_msg + "\tSta. Loc. %f %f %f\n GMT offset %f" % (lon, lat, elevation, GMT_Diff)
  print error_msg


def cmd_write_data(file, data, fields, start_date, elevation):
  for i in range(len(data)):
    # output data according to fields
    file.write(" ")
    if fields.rel_date == 1:
      file.write(" %10.6f" % (data[i].time,))
    if fields.abs_date == 1:
      file.write(" %20.6f" % (data[i].time + start_date,))
    if fields.time_str == 1:
      (year, month, day, h, m, s) = grav_util.un_jday(data[i].jul_day)
      file.write(" %02d/%02d/%04d %02d:%02d:%02d"%(month,day,year, h,m,s))
    if fields.station_id == 1:
      file.write(" %25s" % (data[i].station_id,))
    if fields.gravity == 1:
      file.write(" %8.3f" % (data[i].gravity,))
    if fields.tilt_x == 1:
      file.write(" %6d" % (data[i].tilt_x,))
    if fields.tilt_y == 1:
      file.write(" %6d" % (data[i].tilt_y,))
    if fields.temp == 1:
      file.write(" %6.2f" % (data[i].temp,))
    if fields.tetc == 1:
      (year, month, day, hour, minute, second)=grav_util.un_jday(data[i].jul_day)
      data[i].elevation = elevation
      C = earth_tide(year, month, day, hour, minute, second,
	data[i].Lon, data[i].Lat, data[i].elevation, 0.0,
	data[i].GMT_Diff)
      if C == 3e38:
	# Error in input values!
	cmd_tide_error(i, data[i].jul_day, year, month, day, hour, minute,
			second, data[i].Lat,
		  	data[i].Lon, data[i].elevation, data[i].GMT_Diff)
	C = 0.0
      file.write(" %6.3g" % (C/1000.0,))
    if fields.lat == 1:
      file.write(" %7.3f" % (data[i].Lat,))
    if fields.lon == 1:
      file.write(" %8.3f" % (data[i].Lon,))
    if fields.GMT == 1:
      file.write(" %8.3f" % (data[i].GMT_Diff,))
    file.write("\n")



#
# BEGIN MAIN CODE
#

start_time = time.time()

fields = Fields()
Apply_Tamura = 0
Verbose = 0
No_Head = 0
elevation = 0.0
Lat = -91
Offset = -99
#
# Parse CMD_LINE opts
if len(sys.argv) < 5:
  print "usage: %s <Meter file> <Gravlog file> <output file> <field_desc> [options]" % sys.argv[0]
  print "where [options] are one or more of:"
  print "[-v] [-q] [-T] [-E elevation] [-O GMT_offset] [-C lat lon]"
  sys.exit()

meterfile = sys.argv[1]
in_file = sys.argv[2]
outfile = sys.argv[3]
field_desc = sys.argv[4]

for i in range(4, len(sys.argv)):
  if sys.argv[i] == "-T":
    Apply_Tamura = 1
  if sys.argv[i] == "-v":
    Verbose = 1
  if sys.argv[i] == "-E":
    elevation = float(sys.argv[i+1])
    i = i+1
  if sys.argv[i] == "-C":
    Lat = float(sys.argv[i+1])
    Lon = float(sys.argv[i+2])
    i = i+2
  if sys.argv[i] == "-O":
    Offset = float(sys.argv[i+1])
    i = i+1
  if sys.argv[i] == "-q":
    No_Head = 1

# parse field_desc
tokens = string.split(field_desc)
for i in range(len(tokens)):
  # big if/elif block
  if tokens[i] == "RD":
    fields.rel_date = 1
  if tokens[i] == "AD":
    fields.abs_date = 1
  if tokens[i] == "TS":
    fields.time_str = 1
  if tokens[i] == "ID":
    fields.station_id = 1
  if tokens[i] == "G":
    fields.gravity = 1
  if tokens[i] == "TX":
    fields.tilt_x = 1
  if tokens[i] == "TY":
    fields.tilt_y = 1
  if tokens[i] == "T":
    fields.temp = 1
  if tokens[i] == "LAT":
    fields.lat = 1
  if tokens[i] == "LON":
    fields.lon = 1
  if tokens[i] == "GMT":
    fields.GMT = 1
  if tokens[i] == "TETC":
    fields.tetc = 1

if Verbose:
  print "Parsed field descriptions"

# Read Raw Data
if Verbose:
  print "Reading input file %s..." % in_file
try:
  data = aliodfile.get_aliod_data(in_file, meterfile)

except:
  print "cannot process file %s! Exiting to system." % (in_file,)
  sys.exit()

if Verbose:
  print "Done."

#
# Convert to relative dates - store minimum day in start_jul_day, and
# then subtract from each data[].time to get times that are less than
# 22000000, etc.
if Verbose:
  sys.stdout.write("Computing relative dates")
  if Lat != -91:
    sys.stdout.write("/resetting lat,lon to %f,%f"%(Lat, Lon))
  if Offset != -99:
    sys.stdout.write("/resetting GMT offset to %f"%Offset)
  sys.stdout.write("...\n")
incoming = []
for i in range(len(data)):
  incoming.append(data[i].jul_day)
start_jul_day = int(min(incoming))+0.5
for i in range(len(data)):
  data[i].time = data[i].jul_day - start_jul_day
  if Lat != -91:
    data[i].Lat = Lat
    data[i].Lon = Lon
  if Offset != -99:
    data[i].GMT_Diff = Offset
    data[i].elevation = elevation

if Verbose:
  print "Done."
#
# Apply Tamura ETC to readings
if Apply_Tamura:
  if Verbose:
    print "Applying Tamura ETC..."
  for i in range(len(data)):
    (year, month, day, hour, minute, second)=grav_util.un_jday(data[i].jul_day)
    C = earth_tide(year, month, day, hour, minute, second,
      data[i].Lon, data[i].Lat, data[i].elevation, 0.0,
      data[i].GMT_Diff)
    if C == 3e38:
      print "Error computing Tamura ETC for record #%d.  No correction applied"%i
      C = 0.0
    data[i].gravity = data[i].gravity + (C/1000.0)

#
# Write output file
if Verbose:
  print "Writing output file..."

try:
  file = open(outfile, "wt")

except:
  print "cannot open %s for output.  Exiting to system.\n" % outfile
  sys.exit()

# write header line
if not No_Head:
  cmd_write_header(file, fields)
# write data
cmd_write_data(file, data, fields, start_jul_day, elevation)

file.flush()
file.close()
end_time = time.time()
if Verbose:
  print "\nDone."
  print "Total elapsed time: %.1f seconds\n" % (end_time - start_time)


