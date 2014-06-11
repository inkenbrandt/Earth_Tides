# Interactive Data Viewer - plots various parameters of the raw data
# set for initial QC of the data

# get plotting package stuff
import tkplot

# system imports
import string, sys, math
import tkFileDialog, tkMessageBox

from cbutton import *

# for readability
#True = 1
#False = 0

class PrivateData:
  def __init__(self):
    self.root = None
    self.station = None
    self.field = None
    self.ptstyle = None
    self.lstyle = None
    self.plot_area = None
    self.data = None
    self.plot_win = None

#
# main - the main procedure that the outside world calls
# data is raw grav. data from CG-3 file (pre-loaded)
def main(data):
  global priv
  priv = PrivateData()
  priv.data = data

  # General flowchart
  # Build GUI
  #   Main window to set plot options
  #     3 buttons at bottom:
  #        1. PLOT - redraw the plot
  #	   2. QUIT - end the session (maybe have confirmation dialog!)
  #        3. CLEAR - erase plot and start again
  #   Plot window to draw plots
  #   Key window with plot key (symbol -> data map)

  # main window
  priv.root = tkplot.Toplevel()
  priv.root.title("Interactive Data Viewer")
  #priv.root.configure()
  priv.main_frame = tkplot.Frame(priv.root, relief="flat", borderwidth=3)

  # Instructions
  instruct_box = tkplot.Frame(priv.root, relief="raised", borderwidth=3)
  instructions = "View Raw Data Module\nv0.8 June 1999"
  tkplot.Label(instruct_box, text=instructions).grid()

  #   Plot fields
  fields_box = tkplot.Frame(priv.main_frame, relief="raised", borderwidth=3)
  tkplot.Label(fields_box, text="Plot field:").grid()
  priv.field = tkplot.StringVar()
  tkplot.Radiobutton(fields_box, var=priv.field, text="Gravity Reading", value="G").grid(sticky="W")
  tkplot.Radiobutton(fields_box, var=priv.field, text="Gravity +- Std. Dev.", value="S").grid(sticky="W")
  tkplot.Radiobutton(fields_box, var=priv.field, text="Tilt X", value="X").grid(sticky="W")
  tkplot.Radiobutton(fields_box, var=priv.field, text="Tilt Y", value="Y").grid(sticky="W")
  tkplot.Radiobutton(fields_box, var=priv.field, text="ETC", value="E").grid(sticky="W")
  tkplot.Radiobutton(fields_box, var=priv.field, text="Duration", value="D").grid(sticky="W")
  tkplot.Radiobutton(fields_box, var=priv.field, text="# Rejected", value="R").grid(sticky="W")

  # Station filter
  filter_box = tkplot.Frame(priv.main_frame, relief="raised", borderwidth=3)
  tkplot.Label(filter_box, text="Plot station:").pack(side="top", fill="both")
  station_sb = tkplot.Scrollbar(filter_box, orient="vertical")
  priv.station = tkplot.Listbox(filter_box, selectmode="multiple", yscrollcommand=station_sb.set)
  priv.station.configure(height=4)
  station_sb.config(command=priv.station.yview)
  station_sb.pack(side="right", fill="y")
  priv.station.pack(side="left", fill="both", expand=1)

  # create unique ID list
  ids = []
  last_id = ""
  for i in range(len(data)):
    if data[i].station_id != last_id:
      last_id = data[i].station_id
      unique = True
      for i in range(len(ids)):
	if ids[i] == last_id:
	  unique = False
      if unique:
	ids.append(last_id)

  # fill the selection box
  priv.station.insert("end", "All stations")
  for i in range(len(ids)):
    priv.station.insert("end", ids[i])

  # Plot style choices
  style_box = tkplot.Frame(priv.main_frame, relief="raised", borderwidth=3)
  tkplot.Label(style_box, text="Plot Style:").grid()
  priv.ptstyle = tkplot.StringVar()
  priv.lstyle = tkplot.StringVar()
  tkplot.Label(style_box, text="Point Type").grid(row=1, column=0, sticky="W")
  tkplot.Label(style_box, text="Line Type").grid(row=1, column=1, sticky="W")
  tkplot.Radiobutton(style_box, var=priv.ptstyle, text="None", value="None").grid(row=2, column=0, sticky="W")
  tkplot.Radiobutton(style_box, var=priv.ptstyle, text="X", value="X").grid(row=3, column=0, sticky="W")
  tkplot.Radiobutton(style_box, var=priv.ptstyle, text="o", value="o").grid(row=4, column=0, sticky="W")
  tkplot.Radiobutton(style_box, var=priv.ptstyle, text="+", value="+").grid(row=5, column=0, sticky="W")
  tkplot.Radiobutton(style_box, var=priv.ptstyle, text="*", value="*").grid(row=6, column=0, sticky="W")
  tkplot.Radiobutton(style_box, var=priv.lstyle, text="None", value="None").grid(row=2, column=1, sticky="W")
  tkplot.Radiobutton(style_box, var=priv.lstyle, text="Solid", value="-").grid(row=3, column=1, sticky="W")
  tkplot.Radiobutton(style_box, var=priv.lstyle, text="Gray12", value="1").grid(row=4, column=1, sticky="W")
  tkplot.Radiobutton(style_box, var=priv.lstyle, text="Gray25", value="2").grid(row=5, column=1, sticky="W")
  tkplot.Radiobutton(style_box, var=priv.lstyle, text="Gray75", value="4").grid(row=6, column=1, sticky="W")

  # bottom buttons
  plot_button = tkplot.Button(priv.main_frame,text="Plot", command=plot_cb)
  clear_button = tkplot.Button(priv.main_frame,text="Clear", command=clear_cb)
  print_button = tkplot.Button(priv.main_frame,text="Save", command=print_cb)
  quit_button = tkplot.Button(priv.main_frame,text="Quit", command=quit_cb)

  # Grid (display) the interface
  instruct_box.grid()
  fields_box.grid(column=0, row=0, rowspan=2, sticky="WENS")
  filter_box.grid(column=1, row=0, sticky="WENS")
  style_box.grid(column=1, row=1, sticky="WENS")
  priv.main_frame.grid()

  plot_button.grid(column=0, row=2)
  clear_button.grid(column=1, row=2)
  print_button.grid(column=0, row=3)
  quit_button.grid(column=1, row=3)

  # Setup Plot window(s)
  priv.plot_win = tkplot.Toplevel()
  priv.plot_win.title("Data Plot")
  priv.plot_area = tkplot.tkplot(priv.plot_win, 480, 640, "white", "black")
  priv.plot_area.show()

  priv.plot_area.title = ""
  priv.plot_area.xlabel = "Time"
  priv.plot_area.xlabeltype = "time"
  priv.plot_area.ylabel = ""
  priv.plot_area.nprec = 3
  priv.plot_area.xstart = 99999.0
  priv.plot_area.xo = 99999.0
  priv.plot_area.xend = 0.0
  priv.plot_area.ystart = 99999.0
  priv.plot_area.yo = 99999.0
  priv.plot_area.yend = 0.0

  # Run mainloop()
  priv.root.mainloop()

  # die on callback
  return

def quit_viewer():
  priv.root.destroy()
  priv.plot_win.destroy()
  priv.root.quit()

def quit_cb(*event):
  # display confirmation/choice dialog box
  if tkMessageBox.askokcancel("Quit", "Confirm data viewer quit?", parent=priv.root):
    quit_viewer()

def clear_cb(*event):
  priv.plot_area.clearplot()
  priv.plot_area.xstart = 99999.0
  priv.plot_area.xo = 99999.0
  priv.plot_area.xend = 0.0
  priv.plot_area.ystart = 99999.0
  priv.plot_area.yo = 99999.0
  priv.plot_area.yend = 0.0

def print_cb(*event):
  out_file = tkFileDialog.asksaveasfilename(title="Save plot as...", initialdir=".", initialfile="plot.ps")
  priv.plot_area.ps_print(out_file, "mono", 1)

def plot_cb(*event):
  # get station ids to plot
  station_filter = True
  indexes = priv.station.curselection()
  try:
    items = map(string.atoi, indexes)
  except ValueError: pass
  station_list = []
  for i in range(len(indexes)):
    station_list.append(priv.station.get(indexes[i]))
    if priv.station.get(indexes[i]) == "All stations":
      station_filter = False

  # create data matrix (data[].(x|y))
  field = priv.field.get()
  data = []
  if station_filter:
    priv.plot_area.title = "Stations %s"%station_list
    # cycle through data records, extracting matching data
    for i in range(len(priv.data)):
      for j in range(len(indexes)):
	if priv.data[i].station_id == priv.station.get(indexes[j]):
	  incoming = tkplot.Point()
	  incoming.x = priv.data[i].date
	  if field == "G":
	    # grav reading
	    incoming.y = priv.data[i].gravity
	  elif field == "S":
	    incoming.y = priv.data[i].gravity + priv.data[i].sigma
	    data.append(incoming)
	    incoming = tkplot.Point()
	    incoming.x = priv.data[i].date
	    incoming.y = priv.data[i].gravity - priv.data[i].sigma
	    data.append(incoming)
	  elif field == "X":
	    incoming.y = priv.data[i].tilt_x
	  elif field == "Y":
	    incoming.y = priv.data[i].tilt_y
	  elif field == "E":
	    incoming.y = priv.data[i].etc
	  elif field == "D":
	    incoming.y = priv.data[i].duration
	  elif field == "R":
	    incoming.y = priv.data[i].rejects
	  data.append(incoming)
  else:
    priv.plot_area.title = "All Stations"
    for i in range(len(priv.data)):
      incoming = tkplot.Point()
      incoming.x = priv.data[i].date
      if field == "G":
	# grav reading
	incoming.y = priv.data[i].gravity
      elif field == "S":
	incoming.y = priv.data[i].gravity + priv.data[i].sigma
	data.append(incoming)
	incoming.y = priv.data[i].gravity - priv.data[i].sigma
      elif field == "X":
	incoming.y = priv.data[i].tilt_x
      elif field == "Y":
	incoming.y = priv.data[i].tilt_y
      elif field == "E":
	incoming.y = priv.data[i].etc
      elif field == "D":
	incoming.y = priv.data[i].duration
      elif field == "R":
	incoming.y = priv.data[i].rejects
      data.append(incoming)

  # get data max/min and rescale axes
  xmax = data[0].x
  ymax = data[0].y
  xmin = data[0].x
  ymin = data[0].y
  for i in range(len(data)):
    if data[i].x > xmax:
      xmax = data[i].x
    if data[i].x < xmin:
      xmin = data[i].x
    if data[i].y > ymax:
      ymax = data[i].y
    if data[i].y < ymin:
      ymin = data[i].y

  # scale axes
  Rescale = False
  if priv.plot_area.xend == 0.0 and priv.plot_area.xstart == 99999.0:
    priv.plot_area.xend = xmax
    priv.plot_area.yend = ymax
    priv.plot_area.xstart = xmin
    priv.plot_area.ystart = ymin
    Rescale=True
  if xmax > priv.plot_area.xend:
    priv.plot_area.xend = xmax
    Rescale=True
  if xmin < priv.plot_area.xstart:
    priv.plot_area.xstart = xmin
    Rescale=True
  if ymax > priv.plot_area.yend:
    priv.plot_area.yend = ymax
    Rescale=True
  if ymin < priv.plot_area.ystart:
    priv.plot_area.ystart = ymin
    Rescale=True

  if Rescale:
    priv.plot_area.autoscale(data, 10, 10)
    priv.plot_area.xo = priv.plot_area.xstart
    priv.plot_area.yo = priv.plot_area.ystart

  # plot new data
  priv.plot_area.plot_data(data, priv.lstyle.get(), priv.ptstyle.get())
  # redraw the plot with new axes, etc.
  priv.plot_area.refresh()
  del data

