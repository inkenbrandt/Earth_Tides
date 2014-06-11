##
## File operations for reduce.py, other programs
##

import sys, string, re
import grav_util
from grav_data import *
from fileop import to_float
import fileop

# Read in a raw gravity data file, parse into data object
# data filename is passed as argument, so UI code is elsewhere
def get_cg3_data(filename):
  global nr
  # open the file and read it
  # create file object
  file = open(filename, "rt")

  # now read the file, line by line for memory concerns
  raw_data = []
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
      # control character; maybe EOF mark from CG-3 output
      # skip line
      continue
    if line[0:10] == "----------":
      # beginning of header records
      try:
	head_fields = parse_header(file)
      except StandardError, detail:
	sys.stdout.write("Error processing line %d of data file (HEADER BLOCK): %s\n"%(nr, detail))
	raise

      # line after header end is column titles, which we don't want
      line=file.readline()
      nr = nr+1
      continue
      # end header if
    # not header record, so must be data record
    # parse into fields, and assign to a matrix
    # Must parse based on column # - empty fields are filled with
    # spaces!
    fields = []
    # station id
    fields.append(line[0:7])
    # strip leading whitespace from station name
    fields[0] = string.strip(fields[0])
    # gravity
    fields.append(line[8:16])
    # sigma
    fields.append(line[18:23])
    # tilt_x
    fields.append(line[24:31])
    # tilt_y
    fields.append(line[32:39])
    # temp
    fields.append(line[40:47])
    # etc
    fields.append(line[48:56])
    # duration
    fields.append(line[57:63])
    # rejects
    fields.append(line[64:70])
    # time_str
    fields.append(line[71:79])
    #fields = string.split(line)
    # create an instance of GravityReading with default values
    incoming = GravityReading()
    # set values in incoming, then append onto matrix
    try:
      CG3_fill_gravityreading(incoming, fields, head_fields)
    except StandardError, detail:
      sys.stdout.write("Error processing line %d of data file (DATA BLOCK): %s\n"%(nr, detail))
      raise 

    raw_data.append(incoming)
  # end while loop
  file.close()
  return raw_data
# end get_cg3_data


def parse_header(file):
  global nr
  # file should be a File object that has been opened to the data file
  # header has 12 data records, plus one record of "-" before and
  # after = 14 records total, of which we have read one
  # read lines until end of header
  line=file.readline()
  while line:
    nr = nr+1
    # test for non-data record
    if line[0:10] == "----------": break
    if line[0] == "\n":
      line=file.readline()
      continue
    fields = string.split(line)
    if not fields:
      # no fields, hence essentially an empty record, so skip
      line=file.readline()
      continue
    if fields[0] == "SCINTREX":
      # ID line, with version and Mode type
      ROM_Version = fields[1]
      Mode = fields[4]
      ROM_Release = fields[6]
    elif fields[0] == "Cycle":
      # Cycle Time line, with serial number of unit
      Cycle_time = to_float(fields[2])
      Serial_number = long(to_float(fields[5]))
    elif fields[0] == "Ser":
      # Field mode has no Cycle Time entry, so 1st field is Serial
      # Number
      Cycle_time = -1
      Serial_number = long(to_float(fields[2]))
    elif fields[0] == "Line:":
      # Line, Grid, Job line, with date and Operator code
      Line = long(to_float(fields[1]))
      Grid = long(to_float(fields[3]))
      Job = long(to_float(fields[5]))
      Date_str = fields[7]
      jul_date = grav_util.jul_day(Date_str, "00:00:00")
      Operator = long(to_float(fields[9]))
    elif fields[0] == "GREF.:":
      # GREF line, with XTilt coeff
      GREF = to_float(fields[1])
      Tx_coef = to_float(fields[6])
    elif fields[0] == "GCAL.1:":
      # Gravimeter cal. const. #1 line, w/ YTilt coeff
      GCAL1 = to_float(fields[1])
      Ty_coef = to_float(fields[5])
    elif fields[0] == "GCAL.2:":
      # Grav. Cal. Const. 2, with Latitude
      GCAL2 = to_float(fields[1])
      Lat = to_float(fields[3])
    elif fields[0] == "TEMPCO.:":
      # Temp. coef and longitude
      TEMPCO = to_float(fields[1])
      Long = to_float(fields[4])
    elif fields[1] == "const.:":
      # Drift constant, GMT difference
      drift_const = to_float(fields[2])
      tmp = string.split(fields[5], ".")
      GMT_diff = to_float(tmp[0]) * -1.0
    elif fields[1] == "Correction":
      # Drift correction start time, calibration after N samples
      drift_time = fields[4]
      cal_after = long(to_float(fields[8]))
    elif fields[0] == "Date:":
      # Drift correction start date, tilt correction flag
      drift_date = fields[1]
      tilt_correct = fields[6]
    else: continue # unknown header line, so ignore it
    line=file.readline()
  # end header record read while
  # compute drift start Julian date
  drift_start = grav_util.jul_day(drift_date, drift_time)
  return (ROM_Version, ROM_Release, Mode, Cycle_time, Serial_number, Line, Grid, Job, Operator, jul_date, GREF, GCAL1, GCAL2, Tx_coef, Ty_coef, Lat, Long, GMT_diff, TEMPCO, cal_after, tilt_correct, drift_const, drift_start)
# end parse_header

def CG3_fill_gravityreading(incoming, fields, head_fields):
  # check for '*' on end of fields[1]
  # * at end implies continous tilt correction of value
  if fields[1][-1] == "*":
    fields[1] = fields[1][0:-1]
    tilt_correct = 1
  else:
    tilt_correct = 0
  julian_date = head_fields[9] + grav_util.fract_day(fields[9]) 
  incoming.station_id = fields[0]
  incoming.gravity = to_float(fields[1])
  incoming.sigma = to_float(fields[2])
  incoming.tilt_x = to_float(fields[3])
  incoming.tilt_y = to_float(fields[4])
  incoming.temp = to_float(fields[5])
  try:
    incoming.etc = to_float(fields[6])
  except ValueError:
    incoming.etc = 0.0
  incoming.duration = int(to_float(fields[7]))
  incoming.rejects = int(to_float(fields[8]))
  incoming.time_str = fields[9]
  incoming.meterInfo.ROM_version = head_fields[0]
  incoming.meterInfo.ROM_Release = head_fields[1]
  incoming.meterInfo.Mode = head_fields[2]
  incoming.meterInfo.Cycle_time = head_fields[3]
  incoming.meterInfo.Serial_number = head_fields[4]
  incoming.meterInfo.Line = head_fields[5]
  incoming.meterInfo.Grid = head_fields[6]
  incoming.meterInfo.Job = head_fields[7]
  incoming.meterInfo.Operator = head_fields[8]
  incoming.jul_day = julian_date
  incoming.meterInfo.GRef = head_fields[10]
  incoming.meterInfo.GCal1 = head_fields[11]
  incoming.meterInfo.GCal2 = head_fields[12]
  incoming.meterInfo.TxCo = head_fields[13]
  incoming.meterInfo.TyCo = head_fields[14]
  incoming.meterInfo.Lat = head_fields[15]
  incoming.meterInfo.Lon = head_fields[16]
  incoming.GMT_Diff = head_fields[17]
  incoming.meterInfo.TempCo = head_fields[18]
  incoming.meterInfo.CalAfter = head_fields[19]
  if tilt_correct:
    incoming.tiltCorrect = "Y"
  else:
    incoming.tiltCorrect = "N"
  incoming.meterInfo.DriftCo = head_fields[21]
  incoming.meterInfo.DriftStart = head_fields[22]
# end fill_gravityreading

