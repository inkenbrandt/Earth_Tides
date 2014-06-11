# deltaz - Ground Subsidence correction
#from math import sin, pi

def correction(parameters, data):
  for i in data.keys():
    # Alternate elevation correction, based on a different ellipsoid?
    #E = parameters[data[i].station_id].Z / 30.48 # convert to ft for next eqn
    #phi = data[i].lat * pi/180.0
    #C = (0.09411549 - 0.137789e-3 * sin(phi)**2)*E - 0.67e-8*E**2
    #
    ## gradient is taken to be -308.6 uGal/m = -3.086 uGal/cm
    ## So, with dZ<0 (subsidence), the measured gravity is higher,
    ## but C>0.0 (-0.003986*dZ).  But, correction is subtracted in
    ## reduce.py, so for dZ<0, corrected gravity is smaller, as it
    ## should be.
    C = -0.003086 * parameters[data[i].station_id].Z # mGal/cm
    data[i].dz_correction = C
    data[i].dz = parameters[data[i].station_id].Z
