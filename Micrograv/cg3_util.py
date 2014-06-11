# utility functions for cg3_extract
# expects to be imported as from cg3_util import *
import string, sys
import grav_util
import tamura
import cg3file
import temp_correct

from grav_data import *
from Tkinter import *
from StatusWindow import *

def init_status_win():
  global status
  win = Toplevel()
  win.title("Program Status")
  status = StatusWindow(win, 80, 24)
  status.show()

def write_header(file, buttons):
  file.write("#")
  if buttons.rel_date.query() == 1:
    file.write(" __DAY__")
  if buttons.abs_date.query() == 1:
    file.write(" _JULIAN DATE_")
  if buttons.time_str.query() == 1:
    file.write(" _____DATE/TIME_____")
  if buttons.station_id.query() == 1:
    file.write(" ___STATION ID STRING_____")
  if buttons.gravity.query() == 1:
    file.write(" _GRAVITY")
  if buttons.sigma.query() == 1:
    file.write(" _SIGMA")
  if buttons.tilt_x.query() == 1:
    file.write(" T_X")
  if buttons.tilt_y.query() == 1:
    file.write(" T_Y")
  if buttons.temp.query() == 1:
    file.write(" _TEMP_")
  if buttons.etc.query() == 1:
    file.write(" __ETC_")
  if buttons.tetc.query() == 1:
    file.write(" T_ETC_")
  if buttons.duration.query() == 1:
    file.write(" _DUR")
  if buttons.rejects.query() == 1:
    file.write(" _REJ")
  if buttons.lat.query() == 1:
    file.write(" LATITUD")
  if buttons.lon.query() == 1:
    file.write(" LONGITUD")
  file.write("\n")

def write_data(file, data, buttons, start_date, elevation):
  status.insert(END, "Writing output file...\n")
  index = status.window.index("end linestart")
  lno = int(float(index))-1
  for i in range(len(data)):
    status.replace(lno, "Processing data record %d..." % i)
    # output data according to the checkbuttons
    file.write(" ")
    if buttons.rel_date.query() == 1:
      file.write(" %7.3f" % (data[i].time,))
    if buttons.abs_date.query() == 1:
      file.write(" %13.3f" % (data[i].time + start_date,))
    if buttons.time_str.query() == 1:
      (year, month, day, h, m, s) = grav_util.un_jday(data[i].time + start_date)
      file.write("%02d/%02d/%04d %02d:%02d:%02d"%(month,day,year, h,m,s))
    if buttons.station_id.query() == 1:
      file.write(" %25s" % (data[i].station_id,))
    if buttons.gravity.query() == 1:
      file.write(" %8.3f" % (data[i].gravity,))
    if buttons.sigma.query() == 1:
      file.write(" %6.3f" % (data[i].sigma,))
    if buttons.tilt_x.query() == 1:
      file.write(" %3d" % (data[i].tilt_x,))
    if buttons.tilt_y.query() == 1:
      file.write(" %3d" % (data[i].tilt_y,))
    if buttons.temp.query() == 1:
      file.write(" %6.3f" % (data[i].temp,))
    if buttons.etc.query() == 1:
      file.write(" %6.3f" % (data[i].etc,))
    if buttons.tetc.query() == 1:
      if buttons.flip_lat.query() == 1:
	lat = -1*data[i].meterInfo.Lat
      else:
	lat = data[i].meterInfo.Lat
      if buttons.flip_lon.query() == 1:
	lon = -1*data[i].meterInfo.Lon
      else:
	lon = data[i].meterInfo.Lon
      (year, month, day, hour, minute, second)=grav_util.un_jday(data[i].jul_day)
      data[i].elevation = elevation
      gmt_off = data[i].GMT_Diff
      if buttons.flip_GMT.query() == 1:
	gmt_off = -1*gmt_off
      C = tamura.tide(year, month, day, hour, minute, second,
      data[i].meterInfo.Lon, data[i].meterInfo.Lat, data[i].elevation, 0.0, gmt_off)
      if C == 3e38:
	# Error in input values!
	tide_error(i, data[i].jul_day, year, month, day, hour, minute, second, lat,
		   lon, data[i].elevation, gmt_off)
	C = 0.0
      file.write(" %6.3f" % (C/1000.0,))
    if buttons.duration.query() == 1:
      file.write(" %4d" % (data[i].duration,))
    if buttons.rejects.query() == 1:
      file.write(" %4d" % (data[i].rejects,))
    if buttons.lat.query() == 1:
      file.write(" %7.3f" % (data[i].Lat,))
    if buttons.lon.query() == 1:
      file.write(" %8.3f" % (data[i].Lon,))
    file.write("\n")


def tide_error(i, jul_day, year, month, day, hour, minute, second, lat, lon, elevation, GMT_Diff):
  error_msg = "Error in input parameters to tide correction routine!\n"
  error_msg = error_msg + "Data point #%d\n" % i
  error_msg = error_msg + "Julian Date: %f\n" % jul_day
  error_msg = error_msg + "Parameters are- date/time %f/%f/%f %d:%d:%f\n" % (year,
	  month, day, hour, minute, second)
  error_msg = error_msg + "Sta. Loc. %f %f %f\n GMT offset %f" % (lon, lat, elevation, GMT_Diff)
  tkMessageBox.showerror("ETC Error", error_msg, parent=root)


# modified version of cg3file.py get_cg3_header that adds code for
# a status window
def get_cg3_data(filename):
  status.insert(END, "Reading input file...\n")
  data = cg3file.get_cg3_data(filename)
  status.insert(END, "Finished input file read.\n")
  return data



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

