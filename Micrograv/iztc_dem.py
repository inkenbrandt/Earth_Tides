#!/usr/bin/python

# Given a reduced data file from reduce.py, compute terrain correction
# from DEM data, such as 2m lidar over the site.

# line width:########################################################
VERSION  =  "##            Version 1.0.0 (Apr 2009)                ##";

# system modules
import sys, re
import Tkinter
import tkFileDialog, tkMessageBox, tkSimpleDialog
import time
from types import *
import traceback

# custom modules
import explfileop
from grav_util import Truth
import grav_util
from grav_data import *
import embeddedViewer, StatusWindow
import logger
import terrain

def defaultOptions():
  o = {}
  o["raw_file"] = None
  o["out_file"] = None
  o["dem_file"] = None
  o["max_dist"] = 0.100
  return o

def main():
  global VERSION
  global write, log
  BatchMode = False
  ##Parse command-line args
  for i in range(len(sys.argv)):
    if sys.argv[i] == '-F':
      # batch mode - get input from control file
      BatchMode = True
      try:
	controlfilename = sys.argv[i+1]
      except:
	sys.stderr.write("Must supply control file name; falling back to interactive mode\n")
	BatchMode=False

  options = {}
  if BatchMode:
    # create logger instance 
    log = logger.Logger("izterrain.log")
    # set output function
    write = log.scrn
    options = grokCmdFile(controlfilename)
    if not options:
      # scream and die
      print "CANNOT PARSE COMMAND FILE %s. ABORT."%(controlfilename)
      sys.exit(0)

  else:
    ##Convenience variables
    data_filetypes = (("Reduced Data Files","*.out"), ("All Files","*"))
    dem_filetypes = (("DEM Files","*.hdr"), ("All Files","*"))
    out_filetypes  = (("Inner zone TC Files","*.iztc"), ("All Files","*"))

    ##Fire up the GUI
    root = Tkinter.Tk()
    root.title("Inner Zone Terrain Correction")
    # create status window
    status_win = StatusWindow.StatusWindow(root, 150,30);
    status_win.show()

    # create logger instance 
    log = logger.Logger("izterrain.log", window=status_win)

    # set output function
    write = log.win

    # get default control options
    options = defaultOptions()

  # timestamp the log files
  write("# Started %s\n"%time.asctime(time.localtime(time.time())))
  write("########################################################\n")
  write("##      Inner Zone Terrain Corrections from DEMs      ##\n")
  write("%s\n"%VERSION)
  write("##                   Paul Gettings                    ##\n")
  write("########################################################\n")
  write("\n*** READ REDUCED GRAVITY DATA ***\n\n")

  if not BatchMode:
    write("#-----------------------\n")
    write("# Select the reduced gravity data file.  The file should be in the format\n")
    write("# output by 'reduce.py'; comments are OK.\n")
    write("#-----------------------\n")
    root.update()
  #
  # Read Raw Data
  if BatchMode:
    raw_file = options["raw_file"]
  else:
    raw_file = tkFileDialog.askopenfilename(parent=root, title="Gravity Data File", initialdir=".", filetypes=data_filetypes)

  if not raw_file:
    write( "!!! must enter a processed data filename!\n")
    if not BatchMode:
      tkMessageBox.showerror("No File Name", "Must enter a data filename!")
    sys.exit()

  write(">>> Reading station data file\n")
  try:
    data = explfileop.readData(raw_file)
  except Exception, e:
    write("!!! error processing data file %s\nException: %s\n"%(raw_file, e))
    if not BatchMode:
      tkMessageBox.showerror("Data File Error", "Error processing data file %s!"%raw_file)
    sys.exit()
  write("--> Processed gravity data file '%s' with %d stations\n"%(raw_file, len(data)))

  options["raw_file"] = raw_file

  # get maximum distance
  if BatchMode:
    maxDist = options["max_dist"]
  else:
    title = "Maximum Distance for Correction"
    msg = "Maximum distance for corrections, in km"
    maxDist = tkSimpleDialog.askfloat(title, msg, parent=root)

  if not maxDist:
    write( "!!! must have a maximum distance > 0!\n")
    if not BatchMode:
      tkMessageBox.showerror("Max Distance too small", "Must have a maximum distance >0 km!")
    sys.exit(1)

  options["max_dist"] = maxDist;

  # get DEM file - FloatDEM-compatible format
  if BatchMode:
    dem_file = options["dem_file"]
  else:
    dem_file = tkFileDialog.askopenfilename(parent=root, title="DEM File", initialdir=".", filetypes=dem_filetypes)
  if not dem_file:
    write("!!! No DEM filename given; aborting run!\n")
    if not BatchMode:
      tkMessageBox.showerror("No File Name", "No DEM filename given; aborting run!")
    sys.exit(1)

  if dem_file.endswith(".hdr"):
    name = dem_file[0:len(dem_file)-4]
  else:
    name = dem_file

  # get terrain corrections
  terrain.correct(data, name, write, maxDist)

  # write output file to disk
  if BatchMode:
    out_file = options["out_file"]
  else:
    out_file = tkFileDialog.asksaveasfilename(parent=root, title="Output File", initialdir=".", filetypes=out_filetypes)
  if not out_file:
    write("!!! No output filename given; aborting run!\n")
    if not BatchMode:
      tkMessageBox.showerror("No File Name", "No output filename given; aborting run!")
    sys.exit(1)

  outfile = open(out_file, "wt")
  for k in data.keys():
    stn = data[k]
    outfile.write("%s\t%.3f\n"%(stn.station_id, stn.tc))
  outfile.close()

  # write command file
  outfile = open("izterrain.cmd", "wt")
  for k in options.keys():
    outfile.write( "%-10s\t%s\n"%(k, options[k]) )
  outfile.close()

  write("# Completed at %s\n"%time.asctime(time.localtime(time.time())))

def grokCmdFile(name):
   # read and parse command file
   options = defaultOptions()

   comment = re.compile("^[ \t]*#")

   try:
     file = open(name, "rt")
   except:
     return {}
   if not file:
     return {}

   lines = file.readlines()
   file.close()
   for line in lines:
     # strip newline, leading whitespace
     line = line.strip();
     if comment.search(line):
       # comment line, toss
       continue
     # split and parse
     try:
       (key, val) = line.split(None, 1)
     except ValueError:
       F = line.split()
       key = F[0]
       val = ""
     if key == "max_dist":
       val = float(val)

     options[key] = val
   return options
############
# END MAIN #
############

# RUN IT
try:
  main()
except SystemExit:
  sys.exit(1)
except:
  print "Unhandled exception!  Aborting program."
  print "Results not saved; output files suspect!"
  print "Fix problem and try again."
  print "Program execution traceback follows; submit with bug report."
  traceback.print_exc();
  sys.exit(0);

