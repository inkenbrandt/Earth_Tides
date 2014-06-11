# invert for a piecewise-linear drift function
# requires the Scipy python package for matrix stuff
from scipy import *
from scipy.linalg import *

from grav_data import Station

# interface function for drift.py
def calc_correction(data, repeats, base_stations, tares):
  # create a DriftCorrection instance, and let it run
  DriftFunction = DriftCorrection(data, repeats, base_stations, tares)

  # do inversion
  DriftFunction.drift_inversion()

  # compute drift for each data point
  for i in data.keys():
    data[i].drift_correction = DriftFunction.drift_correction(data[i].time)

  del DriftFunction

class DriftCorrection:
  # data is the averaged, corrected gravity values
  # repeats is a dictionary of station reoccupations
  # base_stations is an array/tuple of station ids that define
  # the linear pieces - i.e. a list of repeated base stations
  def __init__(self, data, repeats, base_stations, tares): 
    # create dictionary of data - makes life easier later
    self.data = {}
    for i in data.keys():
      # we use data[].nodrift_gravity to add in ETC corrections, etc. before inverting
      G = data[i].nodrift_gravity
      # account for tares
      for j in tares.keys():
	if j < data[i].time:
	  G = G + tares[j]
      self.data[data[i].station_id] = Station(data[i].name, G, data[i].sigma, data[i].time)
    self.reps = repeats
    # create time-sorted base_list
    Z={}
    for i in range(len(base_stations)):
      Z[self.data[base_stations[i]].time] = i
    k = Z.keys()
    k.sort()
    self.base_list=[]
    for i in k:
      self.base_list.append(base_stations[Z[i]])
    self.init_matrices()

  def mm(self, a, b):
    return dot(a,b)

  def drift_inversion(self):
    # do the inversion
    #   we use the SciPy extensions to do matrix SVD & inversion
    #   since I really don't want to have to write this
    # compute SVD of A
    (u, q, v) = svd(self.A)
    # reshape q into diagonal matrix
    # get len of q
    (l,) = shape(q)
    z = asarray(identity(l), Float)
    for i in range(l):
      z[i,i] = q[i]
    # compute self.m0 = V(Q^-1)U'd
    self.m0 = dot(v, dot(inv(z), dot(transpose(u), transpose(self.d))))

    # compute self.dp = A*m0
    self.dp = dot(self.A, self.m0)

    # return model
    return self.m0

  def init_matrices(self):
    # here we create the data and operator matrices
    #	we have a dictionary of repeats, and we need to sort the
    #   entries based on time of second station
    # 	so create dictionary mapping time->repeat key
    T = {}
    self.nr = 0
    for i in self.reps.keys():
      for j in range(len(self.reps[i])):
	T[self.data[self.reps[i][j]].time] = [i, j]
	self.nr = self.nr+1
    #	now get keys (which are times) and sort
    K = T.keys()
    K.sort()
    # create data matrix, d
    #	create array instance
    self.d = zeros((len(K),), Float)
    #	fill array with actual values:
    #	iterate over keys, setting self.d[] to dg.
    #	Since data, T, and reps are dictionaries,
    #	we only have a single loop over range(len(K))
    for i in range(len(K)):
      (j, k) = T[K[i]]
      self.d[i] = self.data[self.reps[j][k]].gravity - self.data[j].gravity

    # create operator matrix
    #	create array instance
    self.A = zeros( (len(K), len(self.base_list)-1), Float )
    #	fill array with real values
    #	we need to iterate through each set of repeats (i.e. the same
    #   as for creating d[] above), computing the entries of A.
    #	Algorithm:
    #	1 - we iterate over K, from above; this will iterate over all the
    #	repeats, albeit indirectly through T{}
    #	2 - For each iteration, we compute the drift interval for the first point
    #	of the repeat, then the second point
    #	3 - We fill the correct entry in A[i,j] with the length of time the repeat
    #	spends in the interval.  For point 1, this is t=(end pt) - (data time)
    #		for point 2, this is t = (data point) - (begin pt of interval)
    #	4 - Then we fill in any intervening intervals with the length of the interval
    #	since the repeat spans the whole interval

    base_times = []
    for i in range(len(self.base_list)):
      base_times.append(self.data[self.base_list[i]].time)

    #	Now iterate over data repeats (indirectly)
    for i in range(len(K)):
      # compute interval of first point
      (k, l) = T[K[i]]
      t = self.data[k].time

      if t <= base_times[0]:
	# less than minimum base_time, so set interval1, self.A[i,j]
	self.A[i,0] = base_times[1] - base_times[0]
	self.A[i,0] = self.A[i,0] + (base_times[0] - t)
	interval1 = 0

      for j in range(len(base_times)-1):
	if t > base_times[j] and t <= base_times[j+1]:
	  self.A[i,j] = base_times[j+1] - t
	  interval1 = j
	  break
      # compute interval of second point
      (k, l) = T[K[i]]
      t = self.data[self.reps[k][l]].time
      for j in range(len(base_times)-1):
	if t > base_times[j] and t <= base_times[j+1]:
	  self.A[i,j] = t - base_times[j]
	  break
      if t > base_times[-1]:
	# geater than maximum base_time, so we manually set
	self.A[i,-1] = t - base_times[-1]
	self.A[i,-1] = base_times[-1] - base_times[-2]

      # fill in intervening intervals
      for k in range(interval1+1, j):
	self.A[i,k] = self.data[self.base_list[k+1]].time - self.data[self.base_list[k]].time
    # keep for future reference
    self.K = K
    self.T = T

    #DEBUG
    #print self.d
    #print self.A

  def drift_correction(self, T):
    # here we compute the drift correction for a given time, T
    # we do this by cycling through the model m0 to determine the
    # interval of the time T; then compute the drift for that interval
    # and all previous intervals

    # get list of base station's times
    base_times = []
    for i in range(len(self.base_list)):
      base_times.append(self.data[self.base_list[i]].time)

    # find bracketing interval, if any
    for j in range(len(base_times)-1):
      if T > base_times[j] and T <= base_times[j+1]:
        # we have the interval
	interval = j

    # trap for times outside base stations
    if T <= base_times[0]:
      # less than minimum base time, so we extrapolate with m0[0]
      interval = 0
    if T > base_times[-1]:
      # greater than max. base time, so we extrapolate with last m0
      interval = len(base_times)-1

    # compute correction
    C = 0
    dt = 0.0
    # add in drift for all intervals previous to bracketing one
    #DEBUG:print "_j_ __dt___ __C__ __mo[j]"
    for j in range(0,interval):
      # get correction
      dt = base_times[j+1] - base_times[j]
      C = C + self.m0[j]*dt
    #DEBUG:  print "%3d %.5f %.3f %.5f"%(j, dt, C, self.m0[j])
    # if we are beyond the end repeat, we extrapolate with last slope
    if interval > len(self.m0)-1:
      i = len(self.m0)-1
    else: # add in drift for bracketing interval
      i = interval
    C = C + self.m0[i]*(T - base_times[interval])
    #DEBUG:print "*** %.5f %.3f %.5f"%(dt, C, self.m0[i])

    return C
