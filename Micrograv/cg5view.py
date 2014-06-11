#!/usr/bin/python
# Interactive Data Viewer for raw CG-3M data files

# get plotting package stuff
import tkplot

# get file I/O and utility routines
import cg5file, grav_util

# system imports
import string, sys, math
from Tkinter import *
import tkFileDialog, tkMessageBox

class global_options:
  # class to pass around global parameters, and keep track of where we are
  def __init__(self):
    self.jumpValue = None
    self.data = []
    self.current_id = None
    self.data_file = None
    self.index = 0
    self.ids = []
    self.plot = None
    self.plot_G = None
    self.plot_tilt = None
    self.plot_T = None
    self.plot_E = None

def main(argv):
  global Status

  Status = global_options()

  # main window
  root = Tk()
  root.title("View Data")

  # setup interface
  # 2 windows, one control, one plot
  plot = Toplevel()
  plot.title("Plot")
  Status.plot = plot

  bg = "black"

  Status.plot_G = tkplot.tkplot(plot, 300, 500, "white", "black")
  Status.plot_tilt = tkplot.tkplot(plot, 150, 500, "white", "black")
  Status.plot_T = tkplot.tkplot(plot, 150, 500, "white", "black")
  Status.plot_E = tkplot.tkplot(plot, 150, 500, "white", "black")

  #  setup labels, etc.
  Status.plot_G.xlabeltype = "time"
  Status.plot_tilt.xlabeltype = "time"
  Status.plot_T.xlabeltype = "time"
  Status.plot_E.xlabeltype = "time"
  Status.plot_E.xlabel = "Time since station start"

  Status.plot_G.ylabel = "dG (mGal)"
  Status.plot_tilt.ylabel = "Tilt (arcsec)"
  Status.plot_T.ylabel = "Temperature (mK)"
  Status.plot_E.ylabel = "ETC (mGal)"

  bg = "white"
  fg = "black"

  #   create control window
  title_F = Frame(root, relief=RIDGE, borderwidth=2, background=bg)
  Label(title_F, text="Control Panel", foreground=fg, background=bg).grid()
  title_F.grid(sticky=E+W)

  jump_F = Frame(root, relief=RIDGE, borderwidth=2, background=bg)
  jump_F.grid(sticky=E+W)
  Label(jump_F, text="Jump to Station", foreground=fg, background=bg).grid(columnspan=2, row=0)
  Status.jumpValue = StringVar()
  Entry(jump_F, textvariable=Status.jumpValue, width=6, background=bg,
    foreground=fg).grid(row=1, column=0, sticky=W)
  Button(jump_F, command=jump_cb, text="Find", background=bg,
    foreground=fg).grid(row=1, column=1, sticky=E)

  button_F = Frame(root, relief=RIDGE, borderwidth=2, background=bg)
  button_F.grid(sticky=E+W)
  Label(button_F, text="Previous/Next Station", background=bg,
    foreground=fg).grid(columnspan=2, row=0)
  Button(button_F, command=prev_cb, text="<--", background=bg,
    foreground=fg).grid(row=1, column=0, sticky=W)
  Button(button_F, command=next_cb, text="-->", background=bg,
    foreground=fg).grid(row=1, column=1, sticky=E)

  button_F2 =  Frame(root, relief=FLAT, background=bg)
  button_F2.grid(sticky=E+W)
  Button(button_F2, command=quit_cb, text="Quit", background=bg,
    foreground=fg).grid(row=2, column=0, sticky=W)
  Button(button_F2, command=print_cb, text="Save", background=bg,
    foreground=fg).grid(row=2, column=1, sticky=E)

  # get data filename
  if len(argv) > 1:
    data_file = argv[1]
    try:
      Status.data = cg5file.get_cg5_data(data_file)
    except:
      data_file = tkFileDialog.askopenfilename(parent=root, title="CG-5M data file",
	  initialdir=".", filetypes=(("Text CG-5M files", "*.txt"),
	  ("All files", "*")))
      if not data_file:
	print "Must enter a filename!"
	sys.exit(0)
      try:
	Status.data = cg5file.get_cg5_data(data_file)
      except:
	print "Cannot process file %s!"%data_file
	sys.exit(0)

  else:
    data_file = tkFileDialog.askopenfilename(parent=root, title="CG-5M data file",
	initialdir=".", filetypes=(("Text CG-5M files", "*.txt"),
	("All files", "*")))
    if not data_file:
      print "Must enter a filename!"
      sys.exit(0)
    try:
      Status.data = cg5file.get_cg5_data(data_file)
    except:
      print "Cannot process file %s!"%data_file
      sys.exit(0)

  F = string.split(data_file, "/")
  Status.data_file = F[-1]
  del data_file

  # convert to relative time
  start = grav_util.calc_relative_date(Status.data)

  # create list of sorted unique ids
  ids = {}
  for i in range(len(Status.data)):
    if not ids.has_key(Status.data[i].station_id):
      ids[Status.data[i].station_id] = 1

  Status.ids = ids.keys()
  Status.ids.sort(grav_util.num_sort)

  Status.index = 0
  Status.current_id = Status.ids[Status.index]
  Status.jumpValue.set(Status.current_id)

  Status.plot.bind("<Configure>", resize)

  plot_cb()

  # go
  root.mainloop()

def resize(event):
  global Status
  # window changed size, so need to redraw the plot, using the new size
  # turn off event handler for the configuration
  Status.plot.unbind("<Configure>")

  # set canvas to new window size
  newsize = tkplot.Point()
  newsize.width = event.width
  # get each new height
  newsize.height = int(event.height*0.2)
  Status.plot_tilt.resize(newsize)
  Status.plot_T.resize(newsize)
  Status.plot_E.resize(newsize)
  newsize.height *= 2
  Status.plot_G.resize(newsize)

  Status.plot.bind("<Configure>", resize)

def jump_cb(*event):
  # jump to a given station
  global Status

  for i in range(len(Status.data)):
    if Status.data[i].station_id == Status.jumpValue.get():
      # we have a match, so we can plot something
      Status.current_id = Status.jumpValue.get()
      # find index for this name
      for j in range(len(Status.ids)):
	if Status.ids[j] == Status.current_id:
	  Status.index = j
      plot_cb(event)
      return
  # no match, do nothing
  return

def prev_cb(*event):
  global Status

  if Status.index > 0:
    Status.index = Status.index - 1
    Status.current_id = Status.ids[Status.index]
    Status.jumpValue.set(Status.current_id)
    plot_cb(event)
  else:
    # nothing happens
    return

def next_cb(*event):
  global Status

  if Status.index < len(Status.ids)-1:
    Status.index = Status.index + 1
    Status.current_id = Status.ids[Status.index]
    Status.jumpValue.set(Status.current_id)
    plot_cb(event)
  else:
    # nothing happens
    return

def quit_cb(*event):
  # display confirmation/choice dialog box
  if tkMessageBox.askokcancel("Quit", "Confirm exit?"):
    sys.exit(0)

def print_cb(*event):
  global Status
  # create output name based on station name
  out_file = tkFileDialog.asksaveasfilename(title="Write Postscript to...",
    initialfile = "%s-%s.ps"%(Status.data_file, Status.current_id),
    filetypes=(("Postscript files", "*.ps"), ("All files", "*")))
  # create a long string that holds the PS for all 4 plots
  landscape = 0 # portrait
  P1 = Status.plot_G.postscript("color", landscape) + "\n"
  P2 = Status.plot_tilt.postscript("color", landscape) + "\n"
  P3 = Status.plot_T.postscript("color", landscape) + "\n"
  P4 = Status.plot_E.postscript("color", landscape) + "\n"

  file = open(out_file, "wt")
  file.write(P1+P2+P3+P4)
  file.close()

def plot_cb(*event):
  global Status

  # create data matrices 
  G = []; Gps = []; Gms = []; tx = []; ty = []; T = []; ETC = []
  for i in range(len(Status.data)):
    if Status.data[i].station_id == Status.current_id:
      P = tkplot.Point()
      P.x = Status.data[i].date
      P.y = Status.data[i].gravity;
      G.append(P)
      P = tkplot.Point()
      P.x = Status.data[i].date
      P.y = Status.data[i].gravity + Status.data[i].sigma;
      Gps.append(P)
      P = tkplot.Point()
      P.x = Status.data[i].date
      P.y = Status.data[i].gravity - Status.data[i].sigma;
      Gms.append(P)
      P = tkplot.Point()
      P.x = Status.data[i].date
      P.y = Status.data[i].tilt_x
      tx.append(P)
      P = tkplot.Point()
      P.x = Status.data[i].date
      P.y = Status.data[i].tilt_y
      ty.append(P)
      P = tkplot.Point()
      P.x = Status.data[i].date
      P.y = Status.data[i].temp
      T.append(P)
      P = tkplot.Point()
      P.x = Status.data[i].date
      P.y = Status.data[i].etc
      ETC.append(P)

  # if no matching gravity points, do nothing
  if not G:
    return

  # compute average gravity value
  gbar = 0.0;
  for i in range(len(G)):
    gbar += G[i].y;
  gbar /= len(G);

  # find starting time
  sTime = G[0].x;
  for i in range(len(G)):
    if sTime > G[i].x:
      sTime = x;

  # correct values for average grav & start time
  for i in range(len(G)):
    G[i].y   -= gbar;
    Gps[i].y -= gbar;
    Gms[i].y -= gbar;
    G[i].x   -= sTime;
    Gps[i].x -= sTime;
    Gms[i].x -= sTime;
    tx[i].x -= sTime;
    ty[i].x -= sTime;
    T[i].x -= sTime;
    ETC[i].x -= sTime;

  # create autoscale matrices
  scale_G = []; scale_t = []
  for i in range(len(G)):
    scale_G.append(G[i])
    scale_G.append(Gps[i])
    scale_G.append(Gms[i])
    scale_t.append(tx[i])
    scale_t.append(ty[i])
  minx = getminX(G);
  maxx = getmaxX(G);

  # clear plots
  Status.plot_G.clearplot()
  Status.plot_tilt.clearplot()
  Status.plot_T.clearplot()
  Status.plot_E.clearplot()

  # reset title and scales
  Status.plot_G.title = "File: %s\nStation %s [<g>=%.3f]"%(Status.data_file, Status.current_id, gbar)
  Status.plot_G.autoscale(scale_G, 10, 10)
  Status.plot_G.xstart = minx;
  Status.plot_G.xend = maxx;
  Status.plot_tilt.autoscale(scale_t, 10, 5)
  Status.plot_tilt.xstart = minx;
  Status.plot_tilt.xend = maxx;
  Status.plot_T.autoscale(T, 10, 5)
  Status.plot_T.xstart = minx;
  Status.plot_T.xend = maxx;
  Status.plot_E.autoscale(ETC, 10, 5)
  Status.plot_E.xstart = minx;
  Status.plot_E.xend = maxx;

  Status.plot_G.xo = Status.plot_G.xstart
  Status.plot_G.yo = Status.plot_G.ystart
  Status.plot_T.xo = Status.plot_T.xstart
  Status.plot_T.yo = Status.plot_T.ystart
  Status.plot_E.xo = Status.plot_E.xstart
  Status.plot_E.yo = Status.plot_E.ystart
  Status.plot_tilt.xo = Status.plot_tilt.xstart
  Status.plot_tilt.yo = Status.plot_tilt.ystart

  # plot the data
  for i in range(len(G)):
    # create sets of 3 points, Gps -> G -> Gms
    d = []
    d.append(Gps[i])
    d.append(G[i])
    d.append(Gms[i])
    Status.plot_G.plot_data(d, "-", "None")
  # add "x" at each actual reading
  Status.plot_G.plot_data(G, "None", "x")

  Status.plot_tilt.plot_data(tx, None, "x")
  Status.plot_tilt.plot_data(ty, None, "+")

  Status.plot_T.plot_data(T, None, "o")
  Status.plot_T.plot_data(T, None, "+")

  Status.plot_E.plot_data(ETC, None, "o")
  Status.plot_E.plot_data(ETC, None, "+")


def getmaxX(D):
  # get maximum X value from a set of plotting points D
  maxx = D[0].x;
  for i in range(len(D)):
    if D[i].x > maxx:
      maxx = D[i].x;
  return maxx;

def getminX(D):
  # get minimum X value from a set of plotting points D
  minx = D[0].x;
  for i in range(len(D)):
    if D[i].x < minx:
      minx = D[i].x;
  return minx;


# GO!
main(sys.argv)
