# -*- coding: utf-8 -*-
"""
Created on Wed Aug 07 07:42:40 2013

@author: paulinkenbrandt
"""
import csv
import numpy, scipy
from scipy import signal
import scipy.optimize as optimization
import time
import math
import matplotlib.pyplot as plt
import cmath
import numpy.fft as fft
from operator import itemgetter

###############################################################################
#
############################################################## define variables
#
###############################################################################

impfile = 'dataout4.csv'
impfile2 = 'PW20.csv'

tol = 0.01  #percentage of variance in frequency allowed; default is 2%
r = 3 #well radius in inches
Be = 0.10 #barometric efficiency

#frequencies in cpd
O1 = 0.9295 #principal lunar
K1 = 1.0029 #Lunar Solar
M2 = 1.9324 #principal lunar
S2 = 2.00   #Principal Solar
N2 = 1.8957 #Lunar elliptic

#periods in days
P_M2 = 0.5175
P_O1 = 1.0758

# amplitude factors from Merritt 2004
b_O1 = 0.377
b_P1 = 0.176
b_K1 = 0.531
b_N2 = 0.174
b_M2 = 0.908
b_S2 = 0.423
b_K2 = 0.115

#love numbers and other constants from Agnew 2007
l = 0.0839
k = 0.2980
h = 0.6032
Km = 1.7618 #general lunar coefficient
pi = math.pi #pi

#gravity and earth radius
g = 9.821  #m/s**2
a = 6.3707E6 #m
g_ft = 32.23 #ft
a_ft = 2.0902e7 #ft/s**2

#values to determine porosity from Merritt 2004 pg 56
Beta = 2.32E-8
rho = 62.4


###############################################################################
#
################################################################### import data
#
###############################################################################

#open csv file dataout.csv
data = csv.reader(open(impfile, 'rb'), delimiter=",")
julday, d, t, dial, areal, WDD_tam, wl= [], [], [], [], [], [], []
next(data)

#assign data in csv to arrays
for row in data:
    julday.append(row[0])
    d.append(row[1])
    t.append(row[2])
    wl.append(row[6])

#open csv file data.csv
data1 = csv.reader(open(impfile2, 'rb'), delimiter=",")
lat, longit, elev = [], [], []

for row in data1:
    lat.append(row[2])
    longit.append(row[1])
    elev.append(row[3])

lat =numpy.array(lat)
longit = numpy.array(longit)
elev = numpy.array(elev)

#determine tidal potential Cutillo and Bredehoeft 2010 pg 5 eq 4
f_O1 = -1*math.sin(float(lat[1]))*math.cos(float(lat[1]))
f_M2 = 0.5*math.cos(float(lat[1]))**2


A2_M2 = g_ft*Km*b_M2*f_M2
A2_O1 = g_ft*Km*b_O1*f_O1

#print 'M2 tidal potential (A2)', round(A2_M2,2)
#print 'O1 tidal potential (A2)', round(A2_O1,2)
#print ''

#create arrays for later assignment
xprep = []
yprep = []
zprep = []

yrdty = []
year = []
month = []
day = []
hours =[]
minutes = []
seconds = []

#split date-time (d) into yr,mo,day,hr,min,sec
for i in range(len(d)):
    yrdty.append(time.strptime(d[i],"%m/%d/%Y %H:%M"))
    year.append(yrdty[i].tm_year)
    month.append(yrdty[i].tm_mon)
    day.append(yrdty[i].tm_mday)
    hours.append(yrdty[i].tm_hour)
    minutes.append(yrdty[i].tm_min)
    seconds.append(yrdty[i].tm_sec)

#convert to excel date-time numeric format
xls_date = []
for i in range(len(d)):
    xls_date.append(float(julday[i])-2415018.5)

#convert text from csv to float values
for i in range(len(julday)):
    xprep.append(float(julday[i]))
    yprep.append(float(t[i]))
    zprep.append(float(wl[i]))

#put data into numpy arrays for analysis
xdata = numpy.array(xprep)
ydata = numpy.array(yprep)
zdata = numpy.array(zprep)

#xdata = xdata - xdata[0]
###############################################################################
#
############################################################# Correlate Signals
#
###############################################################################
### define filtering function
def filt(frq,tol,data):
    #define frequency tolerance range
    lowcut = (frq-frq*tol)
    highcut = (frq+frq*tol)
    #conduct fft
    ffta = fft.fft(data)
    bp = ffta[:]
    fftb = fft.fftfreq(len(bp))
    #make every amplitude value 0 that is not in the tolerance range of frequency of interest
    #24 adjusts the frequency to cpd
    for i in range(len(fftb)):
        if (fftb[i]*24)>highcut or (fftb[i]*24)<lowcut:
            bp[i]=0
    #conduct inverse fft to transpose the filtered frequencies back into time series
    crve = fft.ifft(bp)
    yfilt = crve.real
    return yfilt

#filter tidal data
yfilt_O1 = filt(O1,tol,ydata)
yfilt_M2 = filt(M2,tol,ydata)
#filter wl data
zfilt_O1 = filt(O1,tol,zdata)
zfilt_M2 = filt(M2,tol,zdata)


#cormax = numpy.argmax(correl[len(correl)/2-20:len(correl)/2-20])
#print cormax

#plt.figure(12)
#plt.plot(xdata,yfilt_O1,'r')
#plt.twinx()
#plt.plot(xdata,zfilt_O1,'b')
#plt.title('O1')
#plt.figure(27)
#plt.plot(xdata,yfilt_M2,'r')
#plt.twinx()
#plt.plot(xdata,zfilt_M2,'b')
#plt.title('M2')
#plt.figure(29)
#plt.xcorr(yfilt_O1,zfilt_O1,maxlags=10)
#plt.title('Cross Correl O1')
#plt.figure(30)
#plt.xcorr(yfilt_M2,zfilt_M2,maxlags=10)
#plt.title('Cross Correl M2')
#plt.draw()

###############################################################################
#
########################################################### Regression Analysis
#
###############################################################################
#def f3(p, x):
#    #a,b,c = p
#    m = 2.0 * O1 * pi * x
#    y = p[0] + p[1] * (numpy.cos(m))+ p[2] * (numpy.sin(m))
#    return y
#
#def f4(p, x):
#    #a,b,c = p
#    m = 2.0 * M2 * pi * x
#    y = p[0] + p[1] * (numpy.cos(m))+ p[2] * (numpy.sin(m))
#    return y
#
#def f5(p, x):
#    o = 2.0*O1*pi*x
#    m = 2.0*M2*pi*x
#    y = p[0] + p[1] * (numpy.cos(m)) + p[2] * (numpy.sin(m)) + p[3] * (numpy.cos(o))+ p[4] * (numpy.sin(o))
#    return y
##define functions to minimize
#def err3(p,y,x):
#    return y - f3(p,x)
#
#def err4(p,y,x):
#    return y - f4(p,x)
#
#def err5(p,y,x):
#    return y - f5(p,x)
#
def cosM2(p, x):
    m =2*pi*M2*x+p[2]*pi/180
    y = p[0] + p[1]*math.cos(m)
    return y


def err6(p,y,x):
    return y - cosM2(p,x)

def cosO1(p, x):
    m = 2*pi*O1*x+p[2]*pi/180
    y = p[0] + p[1] * math.cos(m)
    return y

def err7(p,y,x):
    return y - cosO1(p,x)
#conducts regression, then calculates amplitude and phase angle
def lstsq(func,y,x):
    #define starting values with x0
   x0 = numpy.array([sum(y)/float(len(y)), 1, 3])
   fit ,chks = optimization.leastsq(func, x0,args=(y, x), maxfev=10000)
##   amp = math.sqrt((fit[1]**2)+(fit[2]**2))      #amplitude
##   phi = numpy.arctan((fit[2]/fit[1]))*(180/pi)   #phase angle
#   amp_M2 = math.sqrt((fit[1]**2)+(fit[2]**2))      #amplitude
#   phi_M2 = numpy.arctan(-1*(fit[2]/fit[1]))*(180/pi)   #phase angle
#   amp_O1 = math.sqrt((fit[3]**2)+(fit[4]**2))      #amplitude
#   phi_O1 = numpy.arctan(-1*(fit[4]/fit[3]))*(180/pi)   #phase angle
   return fit #amp_M2,phi_M2,fit,amp_O1,phi_O1

#water level signal regression
WLO1 = lstsq(err7,zdata,xdata)
WLM2 = lstsq(err6,zdata,xdata)

#tide signal regression
TdO1 = lstsq(err7,ydata,xdata)
TdM2 = lstsq(err6,ydata,xdata)

#calculate phase shift
phase_sft_O1 = WLO1[1] - TdO1[1]
phase_sft_M2 = WLM2[1] - TdM2[1]




delt_O1 = (phase_sft_O1/(O1*360))*24
delt_M2 = (phase_sft_M2/(M2*360))*24

#determine tidal potential Cutillo and Bredehoeft 2010 pg 5 eq 4
f_O1 = math.sin(float(lat[1])*pi/180)*math.cos(float(lat[1])*pi/180)
f_M2 = 0.5*math.cos(float(lat[1])*pi/180)**2

A2_M2 = g_ft*Km*b_M2*f_M2
A2_O1 = g_ft*Km*b_O1*f_O1

#Calculate ratio of head change to change in potential
dW2_M2 = A2_M2/(WLM2[1])
dW2_O1 = A2_O1/(WLO1[1])


print 'amplitudes'
print 'WL M2 amp= ', round(WLM2[1],5)
print 'WL O1 amp= ', round(WLO1[1],5)
#print 'Tide M2 amp =', round(TdM2[0],5)
#print 'Tide O1 amp =', round(TdO1[0],5)
print ''
print 'phase angles'
print 'WL M2 = ', round(WLM2[2],5)
#print 'Tide M2 = ', round(TdM2[1],5)
print 'WL O1 =', round(WLO1[2],5)
#print 'Tide O1 =', round(TdO1[1],5)
#print ''
#print 'water minus tide = phase shift'
#print 'O1 phase shift = ', round(phase_sft_O1,2)
#print 'M2 phase shift = ', round(phase_sft_M2,2)
#print 'O1 phase shift in hours = ', delt_O1
#print 'M2 phase shift in hours = ', delt_M2
print ''
print WLO1[2], WLM2[2]


##Calculate ratio of head change to change in potential
#dW2_M2 = A2_M2/WLM2[0]
#dW2_O1 = A2_O1/WLO1[0]
#
##estimate specific storage
#def SS(rat):
#    return ((1.0-2*0.25)/(0.75))*((2*h-6*l)/(g_ft*a_ft))*rat
#Ss_M2 = SS(dW2_M2)
#Ss_O1 = SS(dW2_O1)
#
##determine porosity from Merritt 2004 pg 56
#porosity_M2 = (Be*Ss_M2)/(Beta*rho)
#porosity_O1 = (Be*Ss_O1)/(Beta*rho)

#print 'porosity = ', round(porosity_M2,4)*100,'%'
#print 'porosity = ', round(porosity_O1,4)*100,'%'
#
#print 'M2 Ss = ', round(Ss_M2,10)
#print 'O1 Ss = ', round(Ss_O1,10)



def curv(Y,P,r):
    rc = (r/12.0)*(r/12.0)
    Y = Y
    X = -1421.15/(0.215746+Y)-13.3401-0.000000143487*Y**4-(9.58311E-16)*Y**8*math.cos(0.9895 + Y + 1421.08/(0.215746 + Y) + 0.000000143487*Y**4)
    T = (X*rc)/P
    return T

Trans_M2 = curv(phase_sft_O1,P_M2,r)
Trans_O1 = curv(phase_sft_M2,P_O1,r)

print 'estimated T (sq ft/day) from M2= ', Trans_M2
print 'estimated T (sq ft/day) from O1= ', Trans_O1
# Y is the phase shift


#B = (3*(1-Be))/(2*(1+v)+al*(1-2*v)*(1-Be))
#
#al = 1 - (Bs/bet)
#
#bet = (-3*B*(1-2*v))/(rho*g*dW2_M2*(2*al*B*(1-2*v)-3(1-v)))

plt.show()

