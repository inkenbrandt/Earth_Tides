#! /usr/bin/python

# GUI-based data extraction from CG-3 raw data
# Uses raw output of CG-3, parses it, and outputs a text file for
# plotting
import Tkinter
import tkFileDialog
import tkMessageBox, tkSimpleDialog
import sys, string

import cg3file
import grav_util
from grav_data import *
from cbutton import *
from tk_indicator import *
from cg3_util import *

class Buttons:
  def __init__(self):
    self.rel_date = Cbutton(root, "Relative Julian Date")
    self.abs_date = Cbutton(root, "Absolute Julian Date") 
    self.time_str = Cbutton(root, "Gregorian Date/Time")
    self.station_id = Cbutton(root, "Station ID")
    self.gravity = Cbutton(root, "Gravity Reading")
    self.sigma = Cbutton(root, "Gravity Std. Deviation")
    self.tilt_x = Cbutton(root, "X Tilt")
    self.tilt_y = Cbutton(root, "Y Tilt")
    self.temp = Cbutton(root, "Temperature")
    self.etc = Cbutton(root, "Meter Earth Tide Corr.")
    self.duration = Cbutton(root, "Duration")
    self.rejects = Cbutton(root, "Rejections")
    self.lat = Cbutton(root, "Latitude")
    self.lon = Cbutton(root, "Longitude")
    self.tetc = Cbutton(root, "Tamura Earth Tide Corr.")
    self.flip_lat = Cbutton(root, "Flip Latitude")
    self.flip_lon = Cbutton(root, "Flip Longitude")
    self.flip_GMT = Cbutton(root, "Flip GMT Offset")

# callbacks for the GUI
def abort_cb(*e):
  sys.exit()

def done_cb(*e):
  elevation = 0.0
  out_name = tkFileDialog.asksaveasfilename(title="Save data as...", initialdir=".", initialfile="data.plt")
  try:
    file = open(out_name, "wt")
  except:
    tkMessageBox.showerror("File Error!", "Cannot open %s for writing. Try again.", parent=root)
    return
  if buttons.tetc.query() == 1:
    # get elevation of file
    elevation = tkSimpleDialog.askfloat("Station Elevation", "Enter Station Elevation (in meters)", parent=root, initialvalue=0.0)
  # write header line
  write_header(file, buttons)
  # write data
  write_data(file, data, buttons, start_jul_day, elevation)
  file.close()
  root.quit()

#
# start up the Tk system, and create the first window
#
root = Tkinter.Tk()
root.title("Data Extraction")

headerbox = Tkinter.Frame(root, relief="raised", borderwidth=3)
Tkinter.Label(headerbox, text="CG-3M DATA EXTRACTION").grid(columnspan=2)
Tkinter.Label(headerbox, text="v1.0 - May 1999").grid(columnspan=2)
Tkinter.Label(headerbox, text="Paul Gettings").grid(columnspan=2)
Tkinter.Label(headerbox, text="University of Utah").grid(columnspan=2)
Tkinter.Label(headerbox, text="Department of\nGeology & Geophysics").grid(columnspan=2)
headerbox.grid(columnspan=2)

indicatorbox = Tkinter.Frame(root, relief="flat", borderwidth=3)
inputlight = indicator(indicatorbox, "Read raw CG-3 file")
etclight = indicator(indicatorbox, "Meter etc removal")
driftlight = indicator(indicatorbox, "Meter drift removal")
datelight = indicator(indicatorbox, "Compute relative dates")
Tkinter.Label(indicatorbox, text="Preprocessing Steps").grid(sticky="W")
inputlight.frame.grid(sticky="W")
etclight.frame.grid(sticky="W")
driftlight.frame.grid(sticky="W")
datelight.frame.grid(sticky="W")
indicatorbox.grid(sticky="W", columnspan=2)


Tkinter.Label(root, text="Output File Columns").grid(columnspan=2)

# create the field buttons
buttons = Buttons()

separator1 = Tkinter.Label(root, text="Data Fields-")
separator2 = Tkinter.Label(root, text="Computed Fields-")
separator3 = Tkinter.Label(root, text="Data Manipulation-")
separator1.grid(columnspan=2)
buttons.rel_date.button.grid(sticky="W", column=0)
buttons.abs_date.button.grid(sticky="W", column=0)
buttons.time_str.button.grid(sticky="W", column=0)
buttons.station_id.button.grid(sticky="W", column=0)
buttons.gravity.button.grid(sticky="W", column=0)
buttons.sigma.button.grid(sticky="W", column=0)
buttons.temp.button.grid(sticky="W", column=0)
init_row = int(buttons.rel_date.button.grid_info().get("row"))
buttons.tilt_x.button.grid(sticky="W", column=1, row=init_row)
buttons.tilt_y.button.grid(sticky="W", column=1, row=init_row+1)
buttons.etc.button.grid(sticky="W", column=1, row=init_row+2)
buttons.duration.button.grid(sticky="W", column=1, row=init_row+3)
buttons.rejects.button.grid(sticky="W", column=1, row=init_row+4)
buttons.lat.button.grid(sticky="W", column=1, row=init_row+5)
buttons.lon.button.grid(sticky="W", column=1, row=init_row+6)
separator2.grid(columnspan=2, row=init_row+7)
buttons.tetc.button.grid(sticky="W", column=0, row=init_row+8)
separator3.grid(columnspan=3)
buttons.flip_lat.button.grid(sticky="W", column=0, row=init_row+10)
buttons.flip_lon.set()
buttons.flip_lon.button.grid(sticky="W", column=1, row=init_row+10)
buttons.flip_GMT.set()
buttons.flip_GMT.button.grid(sticky="W", column=0, row=init_row+11)

b1 = Tkinter.Button(root, text="Write Output File", command=done_cb)
b2 = Tkinter.Button(root, text="Abort", command=abort_cb)
b1.grid(column=0)
b2.grid(column=1, row=int(b1.grid_info().get("row")))

init_status_win()
# Read Raw Data
# get filename dialog
in_file = tkFileDialog.askopenfilename(parent=root,title="Open Raw Data File", initialdir=".", initialfile="data")
#try:
data = get_cg3_data(in_file)

#except:
#  tkMessageBox.showerror("File Error!", "Cannot process file %s! Exiting to system." % (in_file,), parent=root)
#  sys.exit()

inputlight.set()
#
# Preliminary Processing
# remove drift correction applied by meter, if desired.
# remove ETC applied by meter, if desired.
#
# ETC removal
# dialog to remove meter's ETC
if tkMessageBox.askyesno("Remove ETC", "Remove meter-applied Earth Tide correction?", parent=root):
  for i in range(len(data)):
    data[i].gravity = data[i].gravity - data[i].etc
etclight.set()
#
# Drift removal
# dialog to remove meter's drift corr.
if tkMessageBox.askyesno("Remove Drift", "Remove meter-applied drift correction?", parent=root):
  for i in range(len(data)):
    dg = data[i].DriftCo * (data[i].jul_day - data[i].DriftStart)
    data[i].gravity = data[i].gravity + dg
driftlight.set()
#
# Convert to relative dates - store minimum day in start_jul_day, and
# then subtract from each data[].time to get times that are less than
# 22000000, etc.
incoming = []
for i in range(len(data)):
  incoming.append(data[i].jul_day)
start_jul_day = int(min(incoming)) + 0.5
for i in range(len(data)):
  data[i].time = data[i].jul_day - start_jul_day
datelight.set()

# run
root.mainloop()

