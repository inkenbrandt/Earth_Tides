#! /usr/bin/python

# command-line-based data extraction from CG-5 text data
# Uses text output of CG-5, parses it, and outputs a text file for
# plotting
import sys, string
import time

import cg5file
import grav_util
from grav_data import *
from cg3_util import *

import tamura
import temp_correct

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
  if fields.sigma == 1:
    file.write(" _SIGMA")
  if fields.tilt_x == 1:
    file.write(" T_X")
  if fields.tilt_y == 1:
    file.write(" T_Y")
  if fields.temp == 1:
    file.write(" _TEMP_")
  if fields.outside_temp == 1:
    file.write(" O_TEMP")
  if fields.tempCorr == 1:
    file.write(" UCTEMP UCGRAV")
  if fields.etc == 1:
    file.write(" __ETC_")
  if fields.tetc == 1:
    file.write(" T_ETC_")
  if fields.duration == 1:
    file.write(" _DUR")
  if fields.rejects == 1:
    file.write(" _REJ")
  if fields.lat == 1:
    file.write(" LATITUD")
  if fields.lon == 1:
    file.write(" LONGITUD")
  if fields.GMT == 1:
    file.write("  LT-GMT ")
  file.write("\n")

def cmd_write_data(file, data, fields, Verbose, start_date, elevation):
  if Verbose:
    sys.stdout.write("\nProcessing data point ")
  for i in range(len(data)):
    if Verbose:
      sys.stdout.write("%08d\b\b\b\b\b\b\b\b" % i)
      sys.stdout.flush()
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
    if fields.sigma == 1:
      file.write(" %6.3f" % (data[i].sigma,))
    if fields.tilt_x == 1:
      file.write(" %3d" % (data[i].tilt_x,))
    if fields.tilt_y == 1:
      file.write(" %3d" % (data[i].tilt_y,))
    if fields.temp == 1:
      file.write(" %6.3f" % (data[i].temp,))
    if fields.outside_temp == 1:
      file.write(" %6.3f" % (data[i].outsideTemp,))
    if fields.tempCorr == 1:
      if hasattr(data[i], "uncorrected_temp"):
	temp = data[i].uncorrected_temp[1]
	grav = data[i].uncorrected_temp[0]
      else:
	temp = data[i].temp
	grav = data[i].gravity
      file.write(" %6.3f %6.3f"%(temp, grav))
    if fields.etc == 1:
      file.write(" %6.3f" % (data[i].etc,))
    if fields.tetc == 1:
      (year, month, day, hour, minute, second)=grav_util.un_jday(data[i].jul_day)
      data[i].elevation = elevation
      C = tamura.tide(year, month, day, hour, minute, second,
	data[i].meterInfo.Lon, data[i].meterInfo.Lat, data[i].elevation, 0.0,
	data[i].GMT_Diff)
      if C == 3e38:
	# Error in input values!
	cmd_tide_error(i, data[i].jul_day, year, month, day, hour, minute,
			second, data[i].meterInfo.Lat,
		  	data[i].meterInfo.Lon, data[i].elevation, data[i].GMT_Diff)
	C = 0.0
      file.write(" %6.3g" % (C/1000.0,))
    if fields.duration == 1:
      file.write(" %4d" % (data[i].duration,))
    if fields.rejects == 1:
      file.write(" %4d" % (data[i].rejects,))
    if fields.lat == 1:
      file.write(" %7.3f" % (data[i].meterInfo.Lat,))
    if fields.lon == 1:
      file.write(" %8.3f" % (data[i].meterInfo.Lon,))
    if fields.GMT == 1:
      file.write(" %8.3f" % (data[i].GMT_Diff,))
    file.write("\n")


def cmd_tide_error(i, jul_day, year, month, day, hour, minute, second, lat, lon, elevation, GMT_Diff):
  error_msg = "\tError in input parameters to tide correction routine!\n"
  error_msg = error_msg + "\tData point #%d\n" % i
  error_msg = error_msg + "\tJulian Date: %f\n" % jul_day
  error_msg = error_msg + "\tParameters are- date/time %f/%f/%f %d:%d:%f\n" % (year,
	  month, day, hour, minute, second)
  error_msg = error_msg + "\tSta. Loc. %f %f %f\n GMT offset %f" % (lon, lat, elevation, GMT_Diff)
  print error_msg

class Fields:
  def __init__(self):
    self.rel_date = 0
    self.abs_date = 0
    self.time_str = 0
    self.station_id = 0
    self.gravity = 0
    self.sigma = 0
    self.tilt_x = 0
    self.tilt_y = 0
    self.temp = 0
    self.outside_temp = 0
    self.tempCorr = 0
    self.etc = 0
    self.duration = 0
    self.rejects = 0
    self.lat = 0
    self.lon = 0
    self.GMT = 0
    self.tetc = 0

#
# BEGIN MAIN CODE
#

start_time = time.time()

fields = Fields()
Remove_Drift = 0
Remove_ETC = 0
Apply_Tamura = 0
Verbose = 0
Flip_Lon = 0
Flip_Lat = 0
Flip_GMT = 0
No_Head = 0
elevation = 0.0
Lat = -91
Offset = -99
tempThresh = 0.0
#
# Parse CMD_LINE opts
if len(sys.argv) < 4:
  print "usage: %s <infile> <outfile> <field_desc> [options]" % sys.argv[0]
  print "where [options] are one or more of:"
  print "[-d] [-e] [-v] [-E elevation] [-L] [-l] [-G] [-C lat lon] [-T] [-q] [-O GMToffset] [-t TempThresh]"
  sys.exit()

in_file = sys.argv[1]
outfile = sys.argv[2]
field_desc = sys.argv[3]

for i in range(4, len(sys.argv)):
  if sys.argv[i] == "-d":
    Remove_Drift = 1
  if sys.argv[i] == "-e":
    Remove_ETC = 1
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
  if sys.argv[i] == "-L":
    Flip_Lon = 1
  if sys.argv[i] == "-l":
    Flip_Lat = 1
  if sys.argv[i] == "-G":
    Flip_GMT = 1
  if sys.argv[i] == "-O":
    Offset = float(sys.argv[i+1])
    i = i+1
  if sys.argv[i] == "-q":
    No_Head = 1
  if sys.argv[i] == "-t":
    fields.tempCorr = 1
    tempThresh = float(sys.argv[i+1])
    i = i+1

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
  if tokens[i] == "S":
    fields.sigma = 1
  if tokens[i] == "TX":
    fields.tilt_x = 1
  if tokens[i] == "TY":
    fields.tilt_y = 1
  if tokens[i] == "T":
    fields.temp = 1
  if tokens[i] == "OT":
    fields.outside_temp = 1
  if tokens[i] == "ETC":
    fields.etc = 1
  if tokens[i] == "DUR":
    fields.duration = 1
  if tokens[i] == "REJ":
    fields.rejects = 1
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
data = cg5file.get_cg5_data(in_file)

if Verbose:
  print "Done."

#
# Preliminary Processing
# remove drift correction applied by meter, if desired.
# remove ETC applied by meter, if desired.
#
# ETC removal
# dialog to remove meter's ETC
if Remove_ETC:
  if Verbose:
    print "Removing Meter-applied ETC..."
  for i in range(len(data)):
    data[i].gravity = data[i].gravity - data[i].etc

#
# Drift removal
# dialog to remove meter's drift corr.
if Remove_Drift:
  if Verbose:
    print "Removing Meter-applied Drift..."
  for i in range(len(data)):
    dg = data[i].meterInfo.DriftCo * (data[i].jul_day - data[i].meterInfo.DriftStart)
    data[i].gravity = data[i].gravity + dg
#
# Convert to relative dates - store minimum day in start_jul_day, and
# then subtract from each data[].time to get times that are less than
# 22000000, etc.
if Verbose:
  sys.stdout.write("Computing relative dates")
  if Flip_Lon:
    sys.stdout.write("/flipping lon")
  if Flip_Lat:
    sys.stdout.write("/flipping lat")
  if Flip_GMT:
    sys.stdout.write("/flipping GMT")
  if Lat != -91:
    sys.stdout.write("/resetting lat,lon")
  if Offset != -99:
    sys.stdout.write("/resetting GMT offset")
  sys.stdout.write("...\n")
incoming = []
for i in range(len(data)):
  incoming.append(data[i].jul_day)
start_jul_day = int(min(incoming))+0.5
for i in range(len(data)):
  data[i].time = data[i].jul_day - start_jul_day
  if Lat != -91:
    data[i].meterInfo.Lat = Lat
    data[i].meterInfo.Lon = Lon
  if Offset != -99:
    data[i].GMT_Diff = Offset
  if Flip_Lon:
    data[i].meterInfo.Lon = -1*data[i].meterInfo.Lon
  if Flip_Lat:
    data[i].meterInfo.Lat = -1*data[i].meterInfo.Lat
  if Flip_GMT:
    data[i].GMT_Diff = -1*data[i].GMT_Diff

if Verbose:
  print "Done."
#
# Apply Tamura ETC to readings
if Apply_Tamura:
  if Verbose:
    print "Applying Tamura ETC..."
  for i in range(len(data)):
    (year, month, day, hour, minute, second)=grav_util.un_jday(data[i].jul_day)
    data[i].elevation = elevation
    C = tamura.tide(year, month, day, hour, minute, second,
      data[i].meterInfo.Lon, data[i].meterInfo.Lat, data[i].elevation, 0.0,
      data[i].GMT_Diff)
    if C == 3e38:
      print "Error computing Tamura ETC for record #%d.  No correction applied"%i
      C = 0.0
    data[i].gravity = data[i].gravity + (C/1000.0)

#
# Apply temp correction if desired
if tempThresh != 0.0:
  if Verbose:
    print "Correcting Temp. corrections outside +-%f mK"%abs(tempThresh)
  temp_correct.fix(data, tempThresh)

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
cmd_write_data(file, data, fields, Verbose, start_jul_day, elevation)

file.flush()
file.close()
end_time = time.time()
if Verbose:
  print "\nDone."
  print "Total elapsed time: %.1f seconds\n" % (end_time - start_time)
