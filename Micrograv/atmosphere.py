# open atmospheric correction file, read data, and compute
# correction based on time

class Atmosphere:
  def __init__(self):
    self.time = 0.0
    self.pressure = 0.0

def correction(name, data, base_pressure):
  if name == 'none' or not name:
    atm=[]
    incoming = Atmosphere()
    incoming.time = 0.0
    incoming.pressure = 0.0
    atm.append(incoming)
    incoming = Atmosphere()
    incoming.time = 999999.9
    incoming.pressure = 0.0
    atm.append(incoming)
    max_pressure = min_pressure = 0.0
  else:
    try:
      file = open(atm_file, "rt")
    except:
      return 0
    # read the file into the correction array
    lines = file.readlines()
    file.close()
    atm = []
    for i in lines:
      fields = string.split(i)
      incoming = Atmosphere()
      incoming.time = float(fields[0])
      incoming.pressure = float(fields[1])
      atm.append(incoming)
  # compute the atmospheric correction
  for i in range(len(data)):
    min_time = -9999999
    max_time = 99999999
    for j in range(len(atm)):
      if atm[j].time < data[i].time:
	if atm[j].time > min_time:
	  min_time = atm[j].time
	  min_pressure = atm[j].pressure
      if atm[j].time > data[i].time:
	if atm[j].time < max_time:
	  max_time = atm[j].time
	  max_pressure = atm[j].pressure
    dt = max_time - min_time
    dP = max_pressure - min_pressure
    Pt = (dP/dt) * (data[i].time - min_time) + min_pressure
    data[i].atmospheric_correction = -0.00036 * (Pt - base_pressure)

  return 1
