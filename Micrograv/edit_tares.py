#!/usr/bin/python
# edit a tare database

import fileop, tare_core
import grav_util

import sys
from Tkinter import *
import tkFileDialog, tkMessageBox


# fire up Tk
root = Tk()
root.title("Tare Editing")

Label(root, text="Interactive Tare Entry/Edit").grid()
Label(root, text="Copyright 2000, Paul Gettings").grid()
Label(root, text="Dep't of Geology & Geophysics").grid()
Label(root, text="University of Utah").grid()

root.update()

input_file = tkFileDialog.askopenfilename(title="Tare date file",
  initialdir=".", filetypes=(("Tare data files", "*.tare"),
  ("Reduce output files", "*.out"), ("All files", "*")))

if not input_file:
  # no existing tares, so start with empty dict
  tares = {}

else:
  try:
    tares = fileop.get_tares(input_file, 0.0)
  except:
    tkMessageBox.showerror("I/O Error", "Cannot process tare file!")
    tares = {}

#root.destroy()

tares = tare_core.main(tares)

# save tare data
out_name = tkFileDialog.asksaveasfilename(title="Save tare data in...",
  initialdir=".", filetypes=(("Tare data files", "*.tare"),
  ("All files", "*")))

try:
  file = open(out_name, "wt")
except:
  tkMessageBox.showerror("Not saved", "Tare data not saved.")
  sys.exit(0)

fileop.write_tares(tares, 0.0, file)

file.close()
sys.exit(1)
