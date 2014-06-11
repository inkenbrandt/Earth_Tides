# drift_correct.py - the actual drift correction code, minus GUI stuff
from sys import exit

def calc_correction(bid, repeats, data, tares):
# compute drift correction for each point in data[]
  # linear drift function, as a place holder
  print ">>> Using %s and %s as base stations" % (repeats[bid].id1, repeats[bid].id2)
  g1 = g2 = -999999.
  for i in range(len(data)):
    if data[i].station_id == repeats[bid].id1:
      t1 = data[i].time
      g1 = data[i].nodrift_gravity
    elif data[i].station_id == repeats[bid].id2:
      t2 = data[i].time
      g2 = data[i].nodrift_gravity
  # compute drift function and drift correction for each pt.
  if g1 == -999999:
    print "!!! cannot find station %s in data file!" % (repeats[bid].id1,)
    exit(0)
  if g2 == -999999:
    print "!!! cannot find station %s in data file!" % (repeats[bid].id2,)
    exit(0)
  M = (g2-g1) / (t2-t1)
  for i in range(len(data)):
    T = get_tares(data[i].time, tares)
    data[i].drift_correction = M*(data[i].time - t1) - T


def get_tares(t, tares):
# compute total offset of all tares with times <= t
  offset = 0.0
  for i in range(len(tares)):
    if tares[i].time <= t:
      offset = offset + tares[i].offset
  return offset

