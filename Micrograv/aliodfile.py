##
## File operations for Aliod files
##

import sys, string, re
import math
import grav_util
from grav_data import *
import fileop
from fileop import to_float

# Read in an Aliod gravity data file, parse into data object
# data filename is passed as argument, so UI code is elsewhere
def get_aliod_data(dataFile, meterFile, debug=0):
  global nr
  # open the file and read it
  # create file object
  file = open(dataFile, "rt")

  meterInfo = get_aliod_info(meterFile)

  # now read the file, line by line for memory concerns
  raw_data = []
  nr = 0
  while 1:
    line = file.readline()
    if not line: break # EOF reached, return
    nr = nr+1
    # parse the line
    line = line.strip()
    if not line:
      # empty line, so continue
      continue
    if ord(line[0]) > 127 or ord(line[0]) < 32:
      # control character; maybe EOF mark from CG-3 output
      # skip line
      continue
    # parse data line
    incoming = GravityReading()	# defaults to CG-3 settings
    incoming.meterInfo = meterInfo
    fields = line.split(",");
    if len(fields) != 14:
      if debug:
	print "Data file error, line %d: field count wrong"%nr
      continue
    try:
      # GravLog only allows numbers for changing part of name; drop
      # suffix too.  BUT - store as string for initial import!
      incoming.station_id = "%d"%int(fields[0][6:10])
      incoming.jul_day = grav_util.str2jd(fields[1].replace("-","/"), fields[2])
      incoming.time_str = fields[2]
      incoming.notide_gravity = to_float(fields[3])
      # grab gravity with ETC applied; remove later if desired
      incoming.gravity = to_float(fields[4])
      if math.fabs(incoming.gravity) > 50.00:
	if debug:
	  print "Data file error, line %d: gravity out of range"%nr
	continue
      incoming.sigma = 0.001	# ALIOD STORES RAW READINGS, NOT AVERAGES!
      incoming.etc = -1.0* to_float(fields[5])	# flip sign of correction
      incoming.tilt_y = to_float(fields[9])
      incoming.tilt_x = to_float(fields[10])
      incoming.temp = to_float(fields[11])
      if incoming.temp > 60 or incoming.temp < 50:
	if debug:
	  print "Data file error, line %d: temp out of range"%nr
	continue
      incoming.volts = to_float(fields[12])
      incoming.GMT_Diff = incoming.meterInfo.GMT_default
      count2mgal = aliod_counter_to_mGals(to_float(fields[13]), incoming.meterInfo)
      incoming.gravity += count2mgal
      incoming.notide_gravity += count2mgal
    except:
      if debug:
	print "Data file error, line %d: conversion(s) failed"%nr
      continue

    # add to raw_data
    raw_data.append(incoming)
  # end while loop
  file.close()
  return raw_data
# end get_cg3_data


# Read a file of meter-specific constants, including
# counter<=>mGal conversion table.
def get_aliod_info(filename):
  file = open(filename, "rt")
  lines = file.readlines()
  file.close()

  meterInfo = AliodMeterInfo()
  calibrationFlag = 0
  for line in lines:
    if not line.strip(): # empty line, so continue
      continue
    line = line.strip()
    if calibrationFlag:
      if line.upper() == "END":
        calibrationFlag = 0
        continue
      fields = line.split(None, 1)
      meterInfo.calibration[to_float(fields[0])] = to_float(fields[1])
      continue
    try:
      (key, val) = line.split(None, 1)
    except ValueError:
      F = line.split()
      key = F[0]
      val = ""
    if key.upper() == "CALIBRATION":
      calibrationFlag = 1
    elif key.upper() == "CROSS-SENSITIVITY":
      meterInfo.x_sens = to_float(val)
    elif key.upper() == "LONG-SENSITIVITY":
      meterInfo.y_sens = to_float(val)
    elif key.upper() == "TEMPERATURE":
      meterInfo.set_temp = to_float(val)
    elif key.upper() == "GMT-OFFSET":
      meterInfo.GMT_default = to_float(val)
  return meterInfo

def aliod_counter_to_mGals(count, meter_info):
  # interpolate between bracketing count values
  table = meter_info.calibration
  K = table.keys()
  K.sort(grav_util.num_sort)
  start = 0; end = 1;
  for k in K:
    if count < k:
      break;
    else:
      start = k;
  for i in range(0,len(K)):
    if count >= K[i]:
      index = i+1;
  end = K[index]
  mgal=-1
  try:
    mgal = (count - table[start]) * ( (table[end]-table[start])/(end - start) ) + table[start]
  except:
    mgal = 0
  return mgal

