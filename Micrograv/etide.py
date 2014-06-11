# etide - Earth Tide Corrections
# use the best formulas we can, assuming no ETC from the meter!
# this turns out to be Tamura's correction scheme

# for speed, we would like to use the C version of Tamura's
# computation, since that runs orders faster than Python
# But, Python code is portable to all platforms
# so we try to import etc modules (etcmodule.so)
# and if that fails, we use tamura.py
from math import *
import tamura
import grav_util

def correction(data):
  try:
    import etc
    earth_tide = etc.tide
  except:
    earth_tide = tamura.tide

  for i in range(len(data)):
    # compute Tamura ETC
    (year, month, day, hour, minute, second)=grav_util.un_jday(data[i].jul_day)

    C = earth_tide(year, month, day, hour, minute, second,
      data[i].lon, data[i].lat, data[i].elevation, 0.0,
      data[i].GMT_Diff)

    #C = tamura.tide(year, month, day, hour, minute, second, data[i].lon,
#	    data[i].lat, data[i].elevation, 0.0, Offset)
    # Tamura's routine yields results in microgal!
    data[i].etc_correction = C/1000.0

