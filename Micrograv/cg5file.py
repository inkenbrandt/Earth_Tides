##
## File operations for reduce.py, other programs
## CG-5 gravimeter formats
##

###
# WARNING - WE ASSUME CG-5 IS STORING STATIONS IN XYm or XYft FORMAT!!!!
###

import sys, string, re
import grav_util
from grav_data import *
from fileop import to_float
import fileop

class HeaderFields:
  def __init__(self):
    self.survey = "Unknown"
    self.serial = 000000	# serial number
    self.client = "Unknown"
    self.lon = 0.000		# longitude
    self.lat = 0.000		# latitude
    self.zone = -99		# UTM zone
    self.gmt = 13		# GMT offset; original file is west is pos
    self.gref = -1
    self.gcal = -1
    self.xsens = -1
    self.ysens = -1
    self.xoff = -99999
    self.yoff = -99999
    self.tempco = -99999
    self.drift = -99999
    self.drift_start = -1	# compute in julian days!
    self.longman = -1		# if 1, Longman ETC applied, 0 not
    self.tilt_correct = -1	# if 1, Continuous Tilt correction, 0 not
    self.auto_rej = -1		# auto rejection; 1 true, 0 false
    self.terrain = -1		# terrain correction; 1 true, 0 false
    self.seismic = -1		# seismic filter; 1 true, 0 false
    self.rawdata = -1		# raw data stored; 1 true, 0 false

# Read in a text gravity data file, parse into data object
# data filename is passed as argument, so UI code is elsewhere
def get_cg5_data(filename):
  # open the file and read it
  # create file object
  file = open(filename, "rt")

  nr = 0;

  Header = HeaderFields()

  # now read the file, line by line for memory concerns
  raw_data = []	# this will be array of raw readings
  nr = 0
  while 1:
    line = file.readline()
    if not line: break # EOF reached, return
    nr = nr+1
    # parse the line
    if not string.strip(line):
      # empty line, so continue
      continue
    if ord(line[0]) > 127 or ord(line[0]) < 32:
      # control character; corrupt line
      # skip line
      continue
    if line[0] == "/":
      # header record
      try:
        CG5_parse_header(Header, line)
      except StandardError, detail:
	sys.stdout.write("Error processing line %d of data file (HEADER BLOCK): %s\n"%(nr, detail))
	raise
      continue # Next!
      # End header section
    if line[0:4] == "Line":	# line coordinate; toss
      continue

    # data record, so parse as space-delim fields
    fields = string.split(line)
    # create an instance of GravityReading with default values
    # set values in incoming, then append onto matrix
    try:
      incoming = CG5_fill_gravityreading(fields, Header)
    except StandardError, detail:
      sys.stdout.write("Error processing line %d of data file (DATA BLOCK): %s\n"%(nr, detail))
      raise 

    raw_data.append(incoming)
  # end while loop
  file.close()
  return raw_data
# end get_cg5_data


def CG5_parse_header(Header, line):
  fields = string.split(line)
  if len(fields) < 3:
    return	# blank header line
  if fields[1]=="Survey":
    Header.survey = fields[3]
  if fields[1]=="Instrument":
    if len(fields) > 2:
      Header.serial = int(fields[3])
  if fields[1]=="Client:":
    Header.client = fields[2]
  if fields[1] == "Operator:":
    Header.operator = fields[2]
  if fields[1] == "LONG:":
    Header.lon = to_float(fields[2]);
  if fields[1] == "LAT:":
    Header.lat = to_float(fields[2]);
  if fields[1]=="ZONE:":
    Header.zone = int(fields[2]);
  if fields[1]=="GMT":
    if len(fields) > 2:
      Header.gmt = int(to_float(fields[3]));
  if fields[1]=="Gref:":
    Header.gref = to_float(fields[2]);
  if fields[1]=="Gcal1:":
    Header.gcal = to_float(fields[2])
  if fields[1]=="TiltxS:":
    Header.xsens = to_float(fields[2])
  if fields[1]=="TiltyS:":
    Header.ysens = to_float(fields[2])
  if fields[1]=="TiltxO:":
    Header.xoff = to_float(fields[2])
  if fields[1]=="TiltyO:":
    Header.yoff = to_float(fields[2])
  if fields[1]=="Tempco:":
    Header.tempco = to_float(fields[2])
  if fields[1]=="Drift:":
    Header.drift = to_float(fields[2])
  if fields[1]=="DriftTime":
    Header.start_drift_time = fields[3]
  if fields[1]=="DriftDate":	# assume after DriftTime!!!!
    Header.drift_start = grav_util.str2jd(fields[3], Header.start_drift_time)
  if len(fields) < 3:
    return	# blank field for setup params
  if fields[1]=="Tide":
    Header.longman = 0
    if fields[3]=="YES":
      Header.Longman = 1
  if fields[1]=="Cont.":
    Header.tilt_correct = 0	# if 1, Continuous Tilt correction, 0 not
    if fields[3] == "YES":
      Header.tilt_correct = 1	# if 1, Continuous Tilt correction, 0 not
  if fields[1]=="Auto":
    Header.auto_rej = 0		# auto rejection; 1 true, 0 false
    if fields[3] == "YES":
      Header.auto_rej = 1
  if fields[1]=="Terrain":
    Header.terrain = 0		# terrain correction; 1 true, 0 false
    if fields[3]=="YES":
      Header.terrain = 1		# terrain correction; 1 true, 0 false
  if fields[1]=="Seismic":
    Header.seismic = 0		# seismic filter; 1 true, 0 false
    if fields[3]=="YES":
      Header.seismic = 1		# seismic filter; 1 true, 0 false
  if fields[1]=="Raw":
    Header.rawdata = 0		# raw data stored; 1 true, 0 false
    if fields[3]=="YES":
      Header.rawdata = 1		# raw data stored; 1 true, 0 false
  return Header
# end parse_header()

def CG5_fill_gravityreading(fields, header):
  incoming = GravityReading()

  julian_date = grav_util.str2jd(fields[14], fields[11])
  ## Because we assume format is XYm or XYft, we know that field[0] is line, which
  # we drop, and field[1] is station #, but recorded as float.  So, drop to int
  incoming.station_id = str(int(to_float(fields[1])))
  incoming.gravity = to_float(fields[3])
  if header.terrain:
    incoming.gravity = incoming.gravity+to_float(fields[13])
  incoming.sigma = to_float(fields[4])
  incoming.tilt_x = to_float(fields[5])
  incoming.tilt_y = to_float(fields[6])
  incoming.temp = to_float(fields[7])
  try:
    incoming.etc = to_float(fields[8])
  except ValueError:
    incoming.etc = 0.0
  incoming.duration = int(to_float(fields[9]))
  incoming.rejects = int(to_float(fields[10]))
  incoming.time_str = fields[11]
  incoming.meterInfo.Serial_number = header.serial
  incoming.meterInfo.Job = header.survey
  incoming.meterInfo.Operator = header.operator
  incoming.jul_day = julian_date
  incoming.meterInfo.GRef = header.gref
  incoming.meterInfo.GCal1 = header.gcal
  incoming.meterInfo.GCal2 = 0.0	# CG-5 only has Gcal1
  incoming.meterInfo.TxCo = header.xsens
  incoming.meterInfo.TyCo = header.ysens
  incoming.meterInfo.Lat = header.lat
  incoming.meterInfo.Lon = header.lon
  incoming.GMT_Diff = header.gmt*-1.0	# translate W pos to E pos
  incoming.meterInfo.TempCo = header.tempco
  if header.tilt_correct:
    incoming.tiltCorrect = "Y"
  else:
    incoming.tiltCorrect = "N"
  incoming.meterInfo.DriftCo = header.drift
  incoming.meterInfo.DriftStart = header.drift_start
  incoming.outsideTemp = to_float(fields[2])	# assuming we are recording outside temp for fun...

  return incoming
# end fill_gravityreading

