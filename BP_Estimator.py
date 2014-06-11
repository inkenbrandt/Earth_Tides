# -*- coding: utf-8 -*-
"""
Created on Tue Aug 13 08:59:23 2013

@author: paulinkenbrandt
"""

import numpy
import math
import csv
import time
import matplotlib.pyplot as plt
import statsmodels.tsa.tsatools as tools
import sys
from scipy.ndimage import gaussian_filter
import numpy.fft as fft
sys.path.append('C:\\PROJECTS\\Snake_Valley\\PYTHON\\PROCESSING\\New folder')
import tamura

filename='bp_wl_data.csv'
outfile='be_dataout.csv'

lag = 200

#frequencies in cpd
O1 = 0.9295 #principal lunar
K1 = 1.0029 #Lunar Solar
M2 = 1.9324 #principal lunar
S2 = 2.00   #Principal Solar
N2 = 1.8957 #Lunar elliptic


tol = 0.01  #percentage of variance in frequency allowed; default is 2%




#open data file and read in data
data = csv.reader(open(filename, 'rb'), delimiter=",")
d, a, b = [], [], []
# d is the date M/D/YYYY H:MM
#wl is the water level in ft
#bp is the barometric pressure in ft of water
for row in data:
    d.append(row[0])
    a.append(row[1])
    b.append(row[2])





########################################################   date conversion
#function to convert date into julian date
def calc_jday(Y, M, D, h, m, s):
  # Y is year, M is month, D is day
  # h is hour, m is minute, s is second
  # returns decimal day (float)
  Months = [0, 31, 61, 92, 122, 153, 184, 214, 245, 275, 306, 337]
  if M < 3:
    Y = Y-1
    M = M+12
  JD = math.floor((Y+4712)/4.0)*1461 + ((Y+4712)%4)*365
  JD = JD + Months[M-3] + D
  JD = JD + (h + (m/60.0) + (s/3600.0)) / 24.0
  # corrections-
  # 59 accounts for shift of year from 1 Jan to 1 Mar
  # -13 accounts for shift between Julian and Gregorian calendars
  # -0.5 accounts for shift between noon and prev. midnight
  JD = JD + 59 - 13.5
  return(JD)

def jul_day(d):
  # compute decimal julian day from date and time strings
  # date_str is formatted as "DD/MM/YYYY HH:MM"
  # parse the date/time string and call calc_jday() to get
  # the actual Julian Day

    yrdty = time.strptime(d,"%m/%d/%Y %H:%M")
    year = yrdty.tm_year
    month = yrdty.tm_mon
    day = yrdty.tm_mday
    hours = yrdty.tm_hour
    minutes = yrdty.tm_min
    seconds = yrdty.tm_sec
    julday = calc_jday(year,month,day,hours,minutes,seconds)
    return julday

def timestart(d):
  # compute decimal julian day from date and time strings
  # date_str is formatted as "DD/MM/YYYY HH:MM"
  # parse the date/time string and call calc_jday() to get
  # the actual Julian Day

    yrdty = time.strptime(d,"%m/%d/%Y %H:%M")
    year = yrdty.tm_year
    month = yrdty.tm_mon
    day = yrdty.tm_mday
    hours = yrdty.tm_hour
    minutes = yrdty.tm_min
    seconds = yrdty.tm_sec
    hhmm = hours, minutes
    return hhmm


# create a list of julian dates by iterating the jul_day function

yrdty, year, month, day, hours, minutes, seconds, julday = [], [], [], [], [], [], [], []

for i in range(len(d)):
    julday.append(jul_day(d[i]))


for i in range(len(d)):
    yrdty.append(time.strptime(d[i],"%m/%d/%Y %H:%M"))
    year.append(int(yrdty[i].tm_year))
    month.append(int(yrdty[i].tm_mon))
    day.append(int(yrdty[i].tm_mday))
    hours.append(int(yrdty[i].tm_hour))
    minutes.append(int(yrdty[i].tm_min))
    seconds.append(int(0)) #yrdty[i].tm_sec


#converting the julian dates to excel dates
xls_date = []
for i in range(len(d)):
    xls_date.append(float(julday[i])-2415018.5)

wl=[]
for i in range(len(a)):
    wl.append(float(a[i]))

bp =[]
for i in range(len(b)):
    bp.append(float(b[i]))


#put imported data into numpy arrays
xls_date = numpy.array(xls_date)
wl = numpy.asarray(wl)
bp = numpy.asarray(bp)

corr = numpy.corrcoef(bp,wl)
#print corr[0,1]
#plt.figure(1)
#plt.plot(bp,wl,"o")
#plt.show()
#plt.draw()
########################################################## Calculate Earth Tide

t=[]
 #run tidal function
for i in range(len(d)):
    t.append(tamura.tide(year[i], month[i], day[i], hours[i], minutes[i], seconds[i], -113.97, 39.28, 1500.0, 0.0, -7.0))


####################################################



wl_z = []
mn = numpy.mean(wl)
std = numpy.std(wl)
for i in range(len(wl)):
    wl_z.append((wl[i]-mn)/std)

bp_z = []
mn = numpy.mean(bp)
std = numpy.std(bp)
for i in range(len(bp)):
    bp_z.append((bp[i]-mn)/std)

t_z = []
mn = numpy.mean(t)
std = numpy.std(t)
for i in range(len(t)):
    t_z.append((t[i]-mn)/std)

con = numpy.convolve(wl_z,bp_z)

dbp = []
for i in range(len(bp)-1):
    dbp.append(bp[i]-bp[i+1])

dwl = []
for i in range(len(wl)-1):
    dwl.append(wl[i]-wl[i+1])

dt = []
for i in range(len(t)-1):
    dt.append(t[i]-t[i+1])

dbp.append(0)

dwl.append(0)

dt.append(0)


x = numpy.array(dbp)
y = numpy.array(dwl)
z = numpy.array(dt)


##############################################################################
###########################################################################
#
######################################################### Correlate Signals
#
###########################################################################
#### define filtering function
#def filt(frq,tol,data):
#    #define frequency tolerance range
#    lowcut = (frq-frq*tol)
#    highcut = (frq+frq*tol)
#    #conduct fft
#    ffta = fft.fft(data)
#    bp = ffta[:]
#    fftb = fft.fftfreq(len(bp))
#    #make every amplitude value 0 that is not in the tolerance range of frequency of interest
#    #24 adjusts the frequency to cpd
#    for i in range(len(fftb)):
#        if (fftb[i]*spd)>highcut or (fftb[i]*spd)<lowcut:
#            bp[i]=0
#    #conduct inverse fft to transpose the filtered frequencies back into time series
#    crve = fft.ifft(bp)
#    yfilt = crve.real
#    return yfilt
#
##filter tidal data
#yfilt_O1 = filt(O1,tol,ydata)
#yfilt_M2 = filt(M2,tol,ydata)
##filter wl data
#zfilt_O1 = filt(O1,tol,zdata)
#zfilt_M2 = filt(M2,tol,zdata)
#
#zffta = abs(fft.fft(zdata))
#zfftb = abs(fft.fftfreq(len(zdata))*spd)

###########################################################################

"""
sig1 and sig 2 are assumed to be large, 1D numpy arrays
sig1 is sampled at times t1, sig2 is sampled at times t2
t_start, t_end, is your desired sampling interval
t_len is your desired number of measurements
"""
t_start = xls_date[0]
t_end = xls_date[-1]
t_len = (len(xls_date))*60


t = numpy.linspace(t_start, t_end, t_len)
sig1 = numpy.interp(t, xls_date, y)
sig2 = numpy.interp(t, xls_date, z)

#Now sig1 and sig2 are sampled at the same points.

print sig1
print sig2

plt.figure()
#plt.plot(t,sig1)
#plt.twinx()
#plt.plot(t,sig2)
plt.xcorr(sig1,sig2)
plt.show()

"""
Rectify and smooth, so 'peaks' will stand out.
This makes big assumptions about your data;
these assumptions seem true-ish based on your plots.
"""

max_xc = 0
best_shift = 0
for shift in range(-10, 0): #Tune this search range
    xc = (numpy.roll(sig1, shift) * sig2).sum()
    if xc > max_xc:
        max_xc = xc
        best_shift = shift
print 'Best shift:', best_shift
"""
If best_shift is at the edges of your search range,
you should expand the search range.
"""
#############################################################################

# create lag matrix for regression
bpmat = tools.lagmat(x,lag, original='in')
etmat = tools.lagmat(z,lag, original='in')
lamat = numpy.column_stack([bpmat,etmat])
#for i in range(len(etmat)):
#    lagmat.append(bpmat[i]+etmat[i])
#transpose matrix to determine required length
#run least squared regression
sqrd = numpy.linalg.lstsq(bpmat,y)
sqrdlag = numpy.linalg.lstsq(lamat,y)

wlls = sqrd[0]
lagls = sqrdlag[0]

cumls = numpy.cumsum(wlls)
lagcumls =numpy.cumsum(lagls)

ymod = numpy.dot(bpmat,wlls)
lagmod = numpy.dot(lamat,lagls)

alpha = lagls[0:len(lagls)/2]
alpha_cum = numpy.cumsum(alpha)
gamma = lagls[len(lagls)/2:len(lagls)]
gamma_cum = numpy.cumsum(gamma)

lag_time = (xls_date - xls_date[0])*24

print len(wlls), len(sqrdlag)
print len(bpmat), len(etmat), len(lamat)
print len(bpmat[0]),len(etmat[0]),len(alpha),len(gamma)

plt.figure()
plt.subplot(2,1,1)
plt.plot(lag_time[0:len(cumls)],cumls, label='b.p. alone')
plt.plot(lag_time[0:len(cumls)],alpha_cum, label='b.p. when \n considering e.t.')
plt.plot(lag_time[0:len(cumls)],gamma_cum, label='e.t.')
plt.xlabel('lag (hr)')
plt.ylabel('cumulative response function')
plt.legend(loc=4,fontsize='small')
plt.subplot(2,1,2)
plt.plot(lag_time,dwl, label='wl', lw=2)
plt.plot(lag_time,ymod, label='wl modeled w bp')
plt.plot(lag_time,lagmod, 'r--', label='wl modeled w bp&et')
plt.legend(loc=4,fontsize='small')
plt.xlim(0,lag)
plt.ylabel('change (ft)')
plt.xlabel('time (hrs)')
plt.tight_layout()
plt.show()








with open(outfile, "wb") as f:
    filewriter = csv.writer(f, delimiter=',')
    #write header
    header = ['xlday','wl','bp','wl_std','bp_std','dbp','dwl','dt','modeled_y_bp','modWL']
    filewriter.writerow(header)
    for row in range(0,1):
        for i in range(len(d)):
            #you can add more columns here
            filewriter.writerow([xls_date[i],wl[i],bp[i],wl_z[i],bp_z[i],dbp[i],dwl[i],dt[i],ymod[i],lagmod[i]])



outfile2 = 'bephaselag.csv'
with open(outfile2,"wb") as f:
    filewriter =     filewriter = csv.writer(f, delimiter=',')
    #write header
    header = ['wl_lssq','cum_wl_ls','alpha','cum_alpha','gamma','cum_gamma']

    for row in range(0,1):
        for i in range(len(wlls)):
            #you can add more columns here
            filewriter.writerow([wlls[i],cumls[i],alpha[i], alpha_cum[i], gamma[i], gamma_cum[i]])


