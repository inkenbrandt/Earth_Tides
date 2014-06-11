# drift - Instrument Drift
# this is the big one - here we make or break the project

import tkSimpleDialog
import tkMessageBox
import math, string, time
import sys

import tkplot
# Piece-wise linear drift function
import inverse
# Polynomial drift function
import polyfit
# staircase drift function
import staircase

import tare_core

import grav_util
from grav_data import Incoming

# global variable to pass info around
figures = Incoming()

# this code is basically a GUI
# repeats, data, tares are collections from reduce.py, in that format
# options is dict of options, as set in reduce.py; raw_file, order, weighted_drift used
# window is flag to determine if plot windows should be created (>0),
# and/or whether they should be interactive (1 = inter. / 2 = save
# plots and return)
# write is function to output to screen/window/etc.
def correction(repeats, data, tares, options, window, write):
  global figures
  # 1) compute drift function, using tare matrix
  # 2) display dg vs. time
  # 3) display residual between repeats after computing drift
  # 4) allow entry of tare pts on plot
  # 5) go back to 1) until done, then break

  # mangle filename
  t = string.split(options["raw_file"], "/")
  fname = t[-1]
  del t
  timestamp = time.asctime(time.localtime(time.time()))

  figures.order = int(options["order"])
  figures.start_order = int(options["start_order"])
  if figures.order < 0:		# minimum of flat drift fn
    figures.order = 0;
  figures.weighting = grav_util.Truth(options["weighted_drift"])

  # init figures.C to dummy value
  figures.C = [0.0]

  figures.repeats = repeats
  figures.data = data
  figures.tares = tares

  # flag to determine if we plot
  figures.window = window

  # save pointer to write() function
  figures.write = write;

  # plot dg vs time and pre-/post-drift dG
  # 3 windows
  if figures.window:
    win1 = tkplot.Toplevel()
    win2 = tkplot.Toplevel()
    win3 = tkplot.Toplevel()
    win4 = tkplot.Toplevel()
    win5 = tkplot.Toplevel()

    win1.title("Instructions")
    win2.title("Figure 1")
    win3.title("Figure 2")
    win4.title("Figure 3")

    bg = "white"; fg="black"
    figure1 = tkplot.tkplot(win2, 600, 800, bg, fg)
    figure1.show()
    figure2 = tkplot.tkplot(win3, 600, 800, bg, fg)
    figure2.show()
    figure3 = tkplot.tkplot(win4, 600, 800, bg, fg)
    figure3.show()
    figure4 = tkplot.tkplot(win5, 600, 800, bg, fg)
    figure4.show()

    figures.fig1 = figure1
    figures.fig2 = figure2
    figures.fig3 = figure3
    figures.fig4 = figure4
    figures.win1 = win1

    # setup plot parameters
    figure1.title = "Drift Correction vs. Time\n%s\n%s"%(fname, timestamp)
    figure1.xlabel = "Time (hrs)"
    figure1.xlabeltype = "time"
    figure1.ylabel = "Drift Correction (uGal)"
    figure1.nprec = 2

    figure2.title = "g-<g> BEFORE Drift Correction\n%s\n%s"%(fname, timestamp)
    figure2.xlabel = "Time (hrs)"
    figure2.xlabeltype = "time"
    figure2.ylabel = "dg (uGal)"
    figure2.nprec = 2

    figure3.title = "g-<g> AFTER Drift Correction\n%s\n%s"%(fname, timestamp)
    figure3.xlabel = "Time (hrs)"
    figure3.xlabeltype = "time"
    figure3.ylabel = "dg (uGal)"
    figure3.nprec = 2

    figure4.title = "Station Repeat Spans\n%s\n%s"%(fname, timestamp)
    figure4.xlabel = "Time (hrs)"
    figure4.xlabeltype = "time"
    figure4.ylabel = ""
    figure4.nprec = 0
    figure4.ytics(0)

    # create buttons in window 1
    labeltext = '    --- INSTRUCTIONS ---\n\
UPDATE - Updates the figures, recomputing the drift function and dG.\n\
SAVE - Sends a PostScript copy of all figures to disk with fixed filenames.\n\
TARE ENTRY - Enter a tare using the mouse in Figure 2.\n\
TARE EDIT - Edit the times and values of existing tares, or add new ones.\n\
DONE - Return to the text window and finish reduction\n'
    win1.configure(width=400, height=200)
    window_width = int(win1.cget("width"))
    label1 = tkplot.Label(win1, text=labeltext, wraplength=(window_width-10), justify="left")
    # create buttons, and pack it all here
    button1 = tkplot.Button(win1, padx=5, pady=5, text="Update", width=10, height=1, command=apply_cb)
    button2 = tkplot.Button(win1, padx=5, pady=5, text="Save", width=10, height=1, command=print_cb)
    button3 = tkplot.Button(win1, padx=5, pady=5, text="Tare Entry", width=10, height=1, command=tare_cb)
    button5 = tkplot.Button(win1, padx=5, pady=5, text="Tare Edit", width=10, height=1, command=edit_cb)
    button4 = tkplot.Button(win1, padx=5, pady=5, text="Done", width=6, height=1, command=done_cb)
    label1.grid(columnspan=2)
    button1.grid(row=1, column=0)
    button2.grid(row=1, column=1)
    button3.grid(row=2, column=0)
    button5.grid(row=2, column=1)
    button4.grid(row=3, columnspan=2)
    figures.label1 = label1
    figures.button3 = button3
    figures.button5 = button5

    apply_cb(None)
    if figures.window == 2:
      print_cb(None)
    else:
      win1.mainloop()
    win1.destroy()
    win2.destroy()
    win3.destroy()
    win4.destroy()
    win5.destroy()

  else:
    apply_cb(None)

  # reset nodrift_gravity to tare-corrected gravity
  for i in data.keys():
    data[i].nodrift_gravity = data[i].G

  return (figures.order, figures.C)
#
# END CORRECTION
#

def tare_cb(*e):
  global figures
  figures.button3.config(state="disabled")
  old_label = figures.label1.cget("text")
  figures.label1.config(text="Tare Entry Instructions\n1) Using the mouse in FIGURE 2, select 2 points\n2) These points will be used to compute a tare, with time taken from point 1, and offset computed as y2-y1 where y is delta-g, in microgals")
  (x,y) = figures.fig2.get_mouse_click(2)
  #time from first point
  index = figures.data.keys()[0]; D = abs(x[0] - figures.data[index].time);
  for i in figures.data.keys():
    if(abs(x[0] - figures.data[i].time) < D):
      index = i;
      D = abs(x[0] - figures.data[i].time);
  T = x[0] + figures.data[index].start_time;
  figures.tares[T] = (y[1] - y[0]) / 1000.0
  apply_cb(e)
  figures.label1.config(text=old_label)
  figures.button3.config(state="normal")
  figures.button3.update()

def edit_cb(*e):
  global figures
  figures.button5.config(state="disabled")

  figures.tares = tare_core.main(figures.tares)

  figures.button5.config(state="normal")
  figures.button5.update()

def apply_cb(*e):
  global figures
  repeats = figures.repeats
  tares = figures.tares
  data = figures.data
  write = figures.write

  symbols = ["x", "+", "[]", "o"]
  polysymbols = ["-"]
  colors = ["black", "blue", "red", "purple", "green"]

  # account for tares
  tare_core.apply_tares(data, tares);

  # Polynomial drift function
  write("--> [POLYNOMIAL DRIFT FUNCTION]\n");
  for k in data.keys():
    data[k].polyfit_correction = []

  for i in range(figures.start_order,figures.order+1):
    (figures.Cp, L1, L2) = polyfit.correction(data, repeats, i, figures.weighting)
    # copy polyfit drift corrections
    for k in data.keys():
      data[k].polyfit_correction.append(data[k].drift_correction)
    write("    ORDER:%3d PRE-DRIFT- L1:%9g  L2:%9g   POST-DRIFT- L1:%9g  L2:%9g mGal\n"%(i,
      L1[0], L2[0], L1[1], L2[1]));
    write("\t");
    for j in range(len(figures.Cp)):
      write("C[%02d]=%9g "%(j, figures.Cp[j]));
    write("\n");

    # compute "g-dot factor"
    t={}
    for k in data.keys():
      t[data[k].time] = k
    T = t.keys(); T.sort(grav_util.num_sort)
    time=[]
    dg=[]
    for k in T:
      time.append(k)
      dg.append(data[t[k]].drift_correction)
    N = len(time)-1
    mbar = 0.0
    msq = 0.0
    for k in range(N):
      m = ( dg[k+1] - dg[k] )/( time[k+1] - time[k] )
      mbar = mbar + m
      msq = msq + m*m
    mbar = mbar / N
    if mbar != 0:
      gdot = msq / (N*mbar*mbar)
      write("\t.\n");
      write("\tG=%9.6f\n"%gdot);
    else:
      write("\t.\n")
      write("\tG=N/A (m == 0.0)\n")


  # create staircase drift function
  (figures.C, L1[0], L2[0], L1[1], L2[1]) = staircase.correction(data, repeats, figures.weighting)
  write("--> [STAIRCASE DRIFT FUNCTION]\n")
  write("    STEPS:%3d PRE-DRIFT- L1:%9g  L2:%9g   POST-DRIFT- L1:%9g  L2:%9g mGal\n"%(len(figures.C),
         L1[0], L2[0], L1[1], L2[1]))

  # compute "g-dot factor"
  t={}
  for k in data.keys():
    t[data[k].time] = k
  T = t.keys(); T.sort(grav_util.num_sort)
  time=[]
  dg=[]
  for k in T:
    time.append(k)
    dg.append(data[t[k]].drift_correction)
  N = len(time)-1
  mbar = 0.0
  msq = 0.0
  for k in range(N):
    m = ( dg[k+1] - dg[k] )/( time[k+1] - time[k] )
    mbar = mbar + m
    msq = msq + m*m
  mbar = mbar / N
  gdot = msq / (N*mbar*mbar)
  write("\t.\n")
  write("\tG=%9.6f\n"%gdot)

  # calculate linear drift rates in mGal/day
  write("--> [LINEAR DRIFT RATES (uGal/day)]\n")
  k = repeats.keys();
  k.sort(grav_util.num_sort);
  for i in k:
    for j in range(len(repeats[i])):
      dg = data[repeats[i][j]].G - data[i].G
      dt = data[repeats[i][j]].time - data[i].time
      write("    %15s -> %15s ==> %12.3f\n"%(i, repeats[i][j], dg/dt*1000.0));

  # convert residuals to uGals
  for i in range(len(L1)):
    L1[i] = L1[i]*1000.0
    L2[i] = L2[i]*1000.0

  if figures.window:
    figure1 = figures.fig1
    figure2 = figures.fig2
    figure3 = figures.fig3
    figure4 = figures.fig4
    unc_grav = {}
    dc_grav = {}

    # we set up a dict for each pair of repeats
    for i in repeats.keys():
      unc_grav[i] = 0.0
      dc_grav[i] = 0.0
      for j in range(len(repeats[i])):
	unc_grav[repeats[i][j]] = data[repeats[i][j]].G - data[i].G
	dc_grav[repeats[i][j]] = data[repeats[i][j]].G - data[repeats[i][j]].drift_correction
	dc_grav[repeats[i][j]] = dc_grav[repeats[i][j]] - (data[i].G - data[i].drift_correction)

    for i in data.keys():
      if unc_grav.has_key(i):
	continue
      else:
	unc_grav[i] = 0.0
	dc_grav[i] = 0.0

    # create map of unique stations, by looking at
    # repeats dict.
    # each unique station gets a new symbol
    # create dict with unique entry and ids of stations

    # create reversed repeats map
    rmap = {}
    # repeats keys are unique stations!
    for i in repeats.keys():
      rmap[i] = []
      rmap[i].append(i)

    # now go through other stations and add to list
    for i in data.keys():
      match=0
      if not repeats.has_key(i):
	# don't have it as a key, so search full dict
	for j in repeats.keys():
	  for k in range(len(repeats[j])):
	    if repeats[j][k] == i:
	      # match, so add to map under entry j
	      rmap[j].append(i)
	      match = 1
	if not match:
	  # not in repeats, so new station
	  rmap[i] = []
	  rmap[i].append(i)

    # sort the reverse map entries in numeric order
    for i in rmap.keys():
      rmap[i].sort(grav_util.num_sort)

    # create data vectors/dicts d1, d2, d3
    # d1 is drift correction
    # d2 is uncorrected grav (array of arrays)
    # d3 is corrected grav (array of arrays)
    d1 = []; d4 = []
    t={}
    for i in data.keys():
      t[data[i].time] = i
    T = t.keys(); T.sort(grav_util.num_sort)
    for i in T:
      # drift correction
      inc = tkplot.Point()
      inc.y = data[t[i]].drift_correction*1000.0
      inc.x = data[t[i]].time
      d1.append(inc)

    for o in range((figures.order-figures.start_order)+1):
      d4.append([])
      for i in T:
	inc = tkplot.Point()
	inc.x = data[t[i]].time
	inc.y = data[t[i]].polyfit_correction[o]*1000.0
	d4[o].append(inc)

    d5 = []
    for i in range(len(d1)):
      d5.append(d1[i])
    for o in range((figures.order-figures.start_order)+1):
      for i in range(len(d4[o])):
	d5.append(d4[o][i])

    k = rmap.keys()
    # sort in numerical order
    k.sort(grav_util.num_sort)
    cd = []; ud = []
    d2 = []; d3 = []
    for i in k:
      d = []; D = []
      for j in rmap[i]:
	inc = tkplot.Point()
	inc.x = data[j].time
	inc.y = unc_grav[j]*1000
	d.append(inc); ud.append(inc)
	inc = tkplot.Point()
	inc.x = data[j].time
	inc.y = dc_grav[j]*1000
	D.append(inc); cd.append(inc)
      d2.append(d)
      d3.append(D)

    # scale axes
    figure1.autoscale(d5, 10, 10)
    figure1.xo = figure1.xstart
    figure1.yo = figure1.ystart
    figure2.autoscale(ud, 10, 10)
    figure2.xo = figure2.xstart
    figure2.yo = figure2.ystart
    figure3.autoscale(cd, 10, 10)
    dy = figure3.yend - figure3.ystart
    if abs(dy) < 1:	# rescale to at least (-1,1) uGal
      yz = (figure3.yend+figure3.ystart)/2.0
      figure3.yend = yz+1
      figure3.ystart = yz-1
    figure3.xo = figure3.xstart
    figure3.yo = figure3.ystart
    # clear the plots
    figure1.clearplot()
    figure2.clearplot()
    figure3.clearplot()
    # plot data -staircase first, with X and black line
    figure1.color = "black"
    figure1.plot_data(d1, ".", "X")
    figure1.color = "black"
    figure1.plot_data(d1, "-", "")
    # cycle through polynomial drift fns - only plot last 3 orders
    n=0;
    for o in range((figures.order-figures.start_order)+1):
      (s, n) = next_sym(n, polysymbols, colors)
      figure1.color = s.color;
      figure1.plot_data(d4[o], "-", s.symbol)
    figure1.color = "black"

    # cycle through stations
    n = 0;
    for i in k:
      (s, n) = next_sym(n, symbols, colors)
      figure2.color = s.color
      figure3.color = s.color
      figure2.plot_data(d2[n-1], "-", s.symbol)
      figure3.plot_data(d3[n-1], "-", s.symbol)

    figure2.color = "black"
    figure3.color = "black"
    figure2.plot_consty_line(0.0, "-")
    figure3.plot_consty_line(0.0, "-")

    x = (figure1.xstart + figure1.delx/2); y = figure1.ystart + figure1.dely
    figure1.plot_label(x, y-(figure1.dely/5.0), "X - staircase");
    n = 0
    for o in range((figures.order-figures.start_order)+1):
      (s, n) = next_sym(n, polysymbols, colors)
      figure1.color = s.color;
      figure1.plot_label(x, y+(o/5.0*figure1.dely), "%c - poly. order %d"%(s.symbol, o+figures.start_order))
    figure1.color = "black"

    # Add residuals as labels on the plot
    x = figure2.xstart + figure2.delx/2; y = figure2.ystart + figure2.dely
    figure2.plot_label(x, y, "L2 residual: %g uGal\nL1 residual: %g uGal"%(L2[0],L1[0]))
    x = figure3.xstart + figure3.delx/2; y = figure3.ystart + figure3.dely
    figure3.plot_label(x, y, "L2 residual: %g uGal\nL1 residual: %g uGal"%(L2[1],L1[1]))

    # Plot to figure 4: station and repeat as const y value,
    # connected..
    y = 0;
    start = tkplot.Point(); start.x = min(T); start.y = 0;
    end = tkplot.Point(); end.x = max(T); end.y = -1*len(repeats);
    figure4.autoscale([start, end], 10, 10)
    figure4.xo = figure1.xstart
    figure4.yo = figure1.ystart
    figure4.clearplot()
    k = repeats.keys();
    k.sort(grav_util.num_sort);
    for i in k:
      figure4.color = "black"
      d1 = []; 
      inc = tkplot.Point()
      inc.y = y
      inc.x = data[i].time
      figure4.plot_label(inc.x, inc.y, "%s"%i, anchor="se")
      figure4.plot_data([inc], None, "X")
      d1.append(inc)
      for j in range(len(repeats[i])):
	inc = tkplot.Point()
	inc.y = y
	inc.x = data[repeats[i][j]].time
	d1.append(inc)
	figure4.plot_label(inc.x, inc.y, "%s"%repeats[i][j], anchor="se")
	figure4.plot_data([inc], None, "X")
      figure4.plot_data(d1, "-", None);
      y -= 1	# offset next set of repeats 

    figure1.redraw()
    figure2.redraw()
    figure3.redraw()
    figure4.redraw()

def done_cb(*e):
  global figures
  figures.win1.quit()

def print_cb(*e):
  global figures
  old_label = figures.label1.cget("text")
  figures.label1.config(text="Figures 1-4 dumping to files 'drift.ps', 'dg_none.ps', 'dg_drift.ps', and 'repeats.ps' respectively.")
  figures.label1.update_idletasks()
  figures.fig1.ps_print("drift.ps", "color", 1)
  figures.fig2.ps_print("dg_none.ps", "color", 1)
  figures.fig3.ps_print("dg_drift.ps", "color", 1)
  figures.fig4.ps_print("repeats.ps", "color", 1)
  figures.label1.config(text=old_label)

class Symbol:
  def __init__(self):
    self.symbol = ""
    self.color = ""

def next_sym(n, symbols, colors):
  # determine the next symbol and color, depending on n and sizes of
  # "symbols" and "colors"
  # we wrap to first possibility when we hit the end
  # compute # possibilities
  nposs = len(symbols)*len(colors)
  # compute n%nposs to find entry #
  e = n%nposs
  (ce, se) = divmod(e, len(symbols))
  # create entry
  s = Symbol()
  s.symbol = symbols[se]
  s.color = colors[ce]

  return s, n+1

