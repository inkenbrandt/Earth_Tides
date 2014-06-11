# -*- coding: utf-8 -*-
"""
Created on Wed Aug 21 12:19:37 2013

@author: christianhardwick
"""
###############################################################################
# import modules
###############################################################################

import tamura
import time
import numpy as np
import pylab

###############################################################################
ti=time.clock()
print 'Loading file...',
t0=time.clock()

lat=40.772128
lon=-111.937102
elev=1292.0
drift=450.0 # linear drift in microGals per day
GMT=-6 # difference between GMT and local time
g = []
t = []
date = []

infile=open ('CG51drift_SEPT.txt', 'r')
data=np.loadtxt(infile,dtype='string')
for i in data:
    g.append(float(i[3]))
    t.append(i[11])
    date.append(i[14])
tf=time.clock()
print '...Done!',tf-t0, 'seconds'
t0=time.clock
###############################################################################
# split date-time (d) into yr,mo,day,hr,min,sec using time.strptime
###############################################################################
print
print 'Splitting time input arguments...',
t0=time.clock()

yrdty = []
year = []
month = []
day = []
hours =[]
minutes = []
seconds = []
d = []

for i in range(len(t)):
    d.append(date[i]+' '+t[i])
    yrdty.append(time.strptime(d[i],"%Y/%m/%d %H:%M:%S"))
    year.append(yrdty[i].tm_year)
    month.append(yrdty[i].tm_mon)
    day.append(yrdty[i].tm_mday)
    hours.append(yrdty[i].tm_hour)
    minutes.append(yrdty[i].tm_min)
    seconds.append(yrdty[i].tm_sec)
tf=time.clock()
print '...Done!',tf-t0, 'seconds'
t0=time.clock
###############################################################################
# compute theoretical Earth Tide signal [microGal]
###############################################################################
print
print 'Computing Tamura Earth Tide...',
t0=time.clock()

theoretical = []
for i in range(len(t)):
    theoretical.append(tamura.tide(year[i], month[i], day[i], hours[i], minutes[i], seconds[i], lon, lat, elev,0,GMT))
theoretical=np.array(theoretical)
theoretical=-1*theoretical#*1.25 # invert the Tamura tide
tf=time.clock()
print '...Done!',tf-t0, 'seconds'
t0=time.clock
###############################################################################
# attempt to manually remove linear drift from measured data
###############################################################################
print
print 'Removing instrumental drift...',
t0=time.clock()
print 'using',drift,'microGals per day',

days=[]
dayhour=[]
dayminute=[]
daysecond=[]
drift0=[]
step=0 # initialize day counter
days.append(step) # initialize day counter with 0 for use in the "if loop"
  
for i in range(len(day)-1):
    if day[i+1] != day[i]:
        step=step+1
    else:
        step=step
    days.append(float(step)) # count the number of days, store in array

for i in range(len(day)):
    dayhour.append(float(hours[i])/24)
    dayminute.append(float(minutes[i])/(24*60))
    daysecond.append(float(seconds[i])/(24*60*60))
    drift0.append(days[i]+dayhour[i]+dayminute[i]+daysecond[i]) # decimal days
    
    
driftt=np.array(drift0) # converto to array for ease of math manipulations
dstart=driftt[0]
driftt=driftt-dstart # remove static offset so that origin time = 0


offset=g[0]-theoretical[0]/1000 # calculate initial offset between relative gravity and Earth tide
g=np.array(g)
glin=(g[:]-offset)*(1000.0)-driftt[:]*drift # apply offset, convert to microGals and apply linear drift correction

tf=time.clock()
print '...Done!',tf-t0, 'seconds'
###############################################################################
# Plot the results
###############################################################################
print
print 'Total time:', tf-ti, 'seconds'
print
print 'Plotting results...'


y=theoretical[:]
x=driftt[:]
pylab.figure(0)
pylab.plot(x,glin,'.y')
pylab.plot(x,y,'-b',linewidth=1)
#pylab.axis([0,25,-150,150])
pylab.ylabel('microGals')
pylab.xlabel('Days')
pylab.legend(('CG5 measurement','Tamura theoretical tide'))
pylab.show()
tf=time.clock()

pylab.figure(1)




pylab.figure(2)
diff=glin[:]-y[:] # compute residual
y2=y[:]#*0.1 # scale the Earth Tide signal
z=y2[:]*0 # make array to plot zero residual line
pylab.plot(x,diff,'.y') # plot residual
#pylab.plot(x,y2,'-b',linewidth=1) # plot Tamura tide
pylab.plot(x,z,'--k',linewidth=1) # plot zero line
#pylab.axis([0,25,-50,50])
pylab.ylabel('microGals')
pylab.xlabel('Days')
pylab.legend(('residual=obs-pred','Zero residual line'))
pylab.show()
