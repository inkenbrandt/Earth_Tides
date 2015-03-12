# -*- coding: utf-8 -*-
"""
Created on Thu Dec 26 11:34:25 2013

@author: paulinkenbrandt
"""

###############################################################################
# import modules
###############################################################################


import csv
import os
import time
import math
import numpy
import scipy
#import scipy.optimize as op
import scipy.interpolate
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy.fft as fft
import statsmodels.tsa.tsatools as tools
import tamura
import operator
import warnings
from guiqwt.widgets.fit import FitParam, guifit


warnings.simplefilter("ignore", numpy.ComplexWarning)


def skip_first(seq, n):
    #this function is to skip the header rows in the input files
    for i,item in enumerate(seq):
        if i >= n:
            yield item



###########################################################################
"""
INPUT FILES ARE PUT IN BELOW
"""

wlfile='3112.csv'
bpfile='ibpdata.csv'

p = 7.692E5

lag = 100 #this lag is in reference to the barometric efficiency function
tol = 0.008  #percentage of variance in frequency allowed; default is 2%
r = 1 #well radius in inches
Be = 0.10 #barometric efficiency
numb = 5000 # number of values to process
spd = 24 #samples per day hourly sampling = 24
lagt = -7.0 #hours different from UTC (negative indicates west); UT is -7

"""
INPUT FILES END HERE
"""
###############################################################################
# constants
###############################################################################

#frequencies in cpd
O1 = 0.9295 #principal lunar
M2 = 1.9324 #principal lunar

#periods in days
P_M2 = 0.5175
P_O1 = 1.0758

# amplitude factors from Merritt 2004
b_O1 = 0.377
b_M2 = 0.908

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
# import files
###############################################################################
ti=time.clock() # measure time of calculation
print 'Loading file...',
t0=time.clock()

outfile = "c" + wlfile
outfile2 = "c2" + wlfile
wlfiler = csv.reader(open(wlfile, 'rb'), delimiter=",")
dy, u, l, nm, w1, t, vert = [], [], [], [], [], [], []

#remove existing figure files
if os.path.isfile('fs'+os.path.splitext(wlfile)[0]+'.pdf'):
    os.remove('fs'+os.path.splitext(wlfile)[0]+'.pdf')
else:
    print "No old file!"

# read in bp data
bpfiler = csv.reader(open(bpfile, 'rb'), delimiter=",")
v, d2, bp=[], [], []
d3, SG33WDD, PW19S2, PW19M2, MXSWDD = [],[],[],[],[]


#assign data in csv to arrays
for row in wlfiler:
    u.append(row)

for row in bpfiler:
    v.append(row)

#import the wl data
with open(wlfile, 'rb') as tot:
    csvreader = csv.reader(tot)
    for row in skip_first(csvreader, 62):
        dy.append(row[0])
        nm.append(row[1])

#import the bp data
with open(bpfile, 'rb') as tot:
    csvreader = csv.reader(tot)
    for row in skip_first(csvreader, 3):
        d2.append(row[2])
        bp.append(numpy.array(float(row[3])))


#import a smaller part of the wl data
d1=[]
for i in range(len(dy)-numb,len(dy)):
    d1.append(dy[i])
    w1.append(nm[i])

#fill in last line of wl data
w1[-1]=w1[-2]
for i in range(len(w1)):
    if w1[i] is '':
        w1[i]=w1[i-1]

w1 = [float(w1[i]) for i in range(len(w1))]

wl = numpy.array(w1)

#pick well name, lat., long., and elevation data out of header of wl file
well_name = u[0][1]
lon = [float(u[5][1])]*len(d1)
lat = [round(float(u[4][1]),3)]*len(d1)
elv = [round(float(u[10][1])/3.2808,3)]*len(d1)
gmtt = [float(lagt)]*len(d1)

tf=time.clock()
print '...Done!',tf-t0, 'seconds'
t0=time.clock

##############################################################################
# prepare time variables for tidal function
##############################################################################
ti=time.clock() # measure time of calculation
print 'Making time...',
t0=time.clock()

df1="%Y-%m-%d %H:%M:%S"  #date formats
df2="%m/%d/%Y %H:%M"


def datecomp(d,df):
    '''split information in date text into individual peices
    \n  d = date data
    \n  df = date format
    \n  examples of date format: "%Y-%m-%d %H:%M:%S" "%m/%d/%Y %H:%M"
    \n  use formats from the time.striptime function'''
    yrdty = [time.strptime(d[i],df) for i in range(len(d))]
    yrs = [int(yrdty[i].tm_year) for i in range(len(d))]
    mns = [int(yrdty[i].tm_mon) for i in range(len(d))]
    dys = [int(yrdty[i].tm_mday)for i in range(len(d))]
    hrs = [int(yrdty[i].tm_hour)for i in range(len(d))]
    mins = [int(yrdty[i].tm_min)for i in range(len(d))]
    secs = [int(yrdty[i].tm_sec)for i in range(len(d))]
    return yrdty,yrs,mns,dys,hrs,mins,secs


wldt = datecomp(d1,df1)
bpdt = datecomp(d2,df1)
etdt = datecomp(d3,df2)

def calc_jday(Y, M, D, h, m, s):
    ''' Y is year, M is month, D is day
    \n  h is hour, m is minute, s is second
    \n  returns decimal day (float)'''
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
    #convert to excel date-time numeric format
    XLS = JD - 2415018.5
    return JD,XLS


# create a list of excell dates
wlt = numpy.array([float(calc_jday(wldt[1][i],wldt[2][i],wldt[3][i],wldt[4][i],wldt[5][i],wldt[6][i])[1]) for i in range(len(d1))])
bpt = numpy.array([float(calc_jday(bpdt[1][i],bpdt[2][i],bpdt[3][i],bpdt[4][i],bpdt[5][i],bpdt[6][i])[1]) for i in range(len(d2))])

tf=time.clock()
print '...Done!',tf-t0, 'seconds'
t0=time.clock

##############################################################################
# run tidal function
##############################################################################

ti=time.clock() # measure time of calculation
print 'Calling Tamura Code...',
t0=time.clock()

#iterate tamura code over each measurement
t = [tamura.tide(wldt[1][i], wldt[2][i], wldt[3][i], wldt[4][i], wldt[5][i], wldt[6][i], lon[i], lat[i], elv[i], 0.0, gmtt[i]) for i in range(len(d1))]

areal = [(t[i]*p*1E-5) for i in range(len(t))]                            # areal determine areal strain from Agnew 2007, units in mm
potential = [(-318.49681664*t[i] - 0.50889238) for i in range(len(t))]
WDD_tam = numpy.array([(t[i]*(-0.99362956469)-7.8749754) for i in range(len(t))])       # WDD is used to recreate output from TSoft
dl = [(0.381611837 * t[i] - 0.000609517) for i in range(len(t))]     # dilation from relationship defined using Harrison's code
vert = [(t[i] * 1.692) for i in range(len(t))]                            # determine vertical strain from Agnew 2007; units are in sec squared, meaning results in mm
Grav_tide = [(-1*t[i]) for i in range(len(t))]

tf=time.clock()
print '...Done!',tf-t0, 'seconds'
t0=time.clock

##############################################################################
#  standardize and densify  data
##############################################################################

ti=time.clock() # measure time of calculation
print 'Standardizing Data...',
t0=time.clock()

t1 = numpy.linspace(wlt[0], wlt[-1], len(wlt))  # sets size and interval of time
bp = numpy.array(numpy.interp(t1, bpt, bp))     # interpolate bp data over wl time



def stdnz(A):
    '''this function standardizes data by subtracting the mean and dividing by std dev'''
    A = [(A[i] - numpy.mean(A))/numpy.std(A) for i in range(len(A))]
    return A

def dens(y,x,mult):
    '''this function resamples data at a high rate
    \n y = data
    \n x = time
    \n mult = multiple to increase sampling by'''
    ys = y[len(y)/50:len(y)/8] #shortens data to ease calculation
    xs = x[len(y)/50:len(y)/8]
    new_length = len(xs)*mult
    xexten = numpy.linspace(xs.min(), xs.max(), new_length)
    yexten = scipy.interpolate.interp1d(xs,ys, kind='cubic')(xexten)
    return xexten, yexten

def chn(A):
    '''this function provides user with differences between consecutive values'''
    A = [(A[i] - A[i+1]) for i in range(len(A)-1)]
    A.append(0.0)
    return numpy.array(A)

stwl = stdnz(wl) #standardized wl
stbp = stdnz(bp) #standardized baro press.
stdl = stdnz(dl) #standardized earth tide dilation

# these are change in consecutive standardized values
dwl = chn(stwl)
dbp = chn(stbp)
ddl = chn(stdl)

##densified resampled data
#dnwl = dens(dwl,t1,60)
#dnbp = dens(dbp,t1,60)
#dndl = dens(ddl,t1,60)

tf=time.clock()
print '...Done!',tf-t0, 'seconds'
t0=time.clock

###########################################################################
#  Filter Signals
###########################################################################

ti=time.clock() # measure time of calculation
print 'Filtering Signals...',
t0=time.clock()


def filt(frq,tol,data,spd):
    ''' this function filters signals given a filtering frequency (frq), tolerance (tol), data, and sampling freqency (spd) '''
    #define frequency tolerance range
    lowcut = (frq-frq*tol)
    highcut = (frq+frq*tol)
    #conduct fft
    ffta = fft.fft(data)
    bp2 = ffta[:]
    fftb = fft.fftfreq(len(bp2))
    #make every amplitude value 0 that is not in the tolerance range of frequency of interest
    #24 adjusts the frequency to cpd
    for i in range(len(fftb)):
        #spd is samples per day (if hourly = 24)
        if (fftb[i]*spd)>highcut or (fftb[i]*spd)<lowcut:
            bp2[i]=0
    #conduct inverse fft to transpose the filtered frequencies back into time series
    crve = fft.ifft(bp2)    #complex number returned
    #convert back to frequency domain
    fta = fft.fft(crve)
    rl = fta.real
    im = fta.imag
    mag = [math.sqrt(rl[i]**2 + im[i]**2) for i in range(len(rl))] # magnitude
    phase = [math.atan2(im[i],rl[i]) for i in range(len(rl))]       # phase
    yfilt = crve.real       #real component of complex number
    zfilt = crve.imag       #imaginary component of complex nunmber
    return yfilt, zfilt, crve, mag, phase


#the results of this function are used to compare to the filtered data
#http://stackoverflow.com/questions/6393257/getting-fourier-transform-from-phase-and-magnitude-matlab
#http://dsp.stackexchange.com/questions/8834/retrieving-original-data-from-phase-and-magnitude-of-fourier-transform
def phasefind(data):
    fta = fft.fft(data)
    rl = fta.real
    im = fta.imag
    mag = [math.sqrt(rl[i]**2 + im[i]**2) for i in range(len(rl))]
    phase = [math.atan2(im[i],rl[i]) for i in range(len(rl))]
    return mag, phase

dlmg = phasefind(dl)[0]
wlmg = phasefind(wl)[0]
dlph = phasefind(dl)[1]
wlph = phasefind(wl)[1]
#
#dlphO1 = filt(O1,tol,dl,spd)[4]
#dlphM2 = filt(M2,tol,dl,spd)[4]
#wlphO1 = filt(O1,tol,wl,spd)[4]
#wlphM2 = filt(M2,tol,wl,spd)[4]
#dlmgO1 = filt(O1,tol,dl,spd)[3]
#dlmgM2 = filt(M2,tol,dl,spd)[3]
#wlmgO1 = filt(O1,tol,wl,spd)[3]
#wlmgM2 = filt(M2,tol,wl,spd)[3]


#filter tidal data
dl_O1 = filt(O1,tol,dl,spd)
dl_M2 = filt(M2,tol,dl,spd)

#filter wl data
wl_O1 = filt(O1,tol,wl,spd)
wl_M2 = filt(M2,tol,wl,spd)

#combine filtered signals
dl_O1_M2 = numpy.array(map(operator.add, dl_O1[0], dl_M2[0]))
wl_O1_M2 = numpy.array(map(operator.add, wl_O1[0], wl_M2[0]))

#### Sites to help with this
# http://stackoverflow.com/questions/13826290/estimating-small-time-shift-between-two-time-series?lq=1
# http://stackoverflow.com/questions/6991471/computing-cross-correlation-function
# http://stackoverflow.com/questions/4688715/find-time-shift-between-two-similar-waveforms?lq=1
# http://stackoverflow.com/questions/6157791/find-phase-difference-between-two-inharmonic-waves?lq=1

##densified filtered data
#dndl_O1 = dens(dl_O1[0],t1,60)
#dnwl_O1 = dens(wl_O1[0],t1,60)
#dndl_M2 = dens(dl_M2[0],t1,60)
#dnwl_M2 = dens(wl_M2[0],t1,60)
#dndl_O1_M2 = dens(dl_O1_M2,t1,60)
#dnwl_O1_M2 = dens(wl_O1_M2,t1,60)


tf=time.clock()
print '...Done!',tf-t0, 'seconds'
t0=time.clock

##########################################################################
# Regression Analysis
###########################################################################
ti=time.clock() # measure time of calculation
print 'Regression analsyses...',
t0=time.clock()


def fitwin(x,y):
    def fit(x, params):
        a, b, c, d = params
        O1 = 0.9295 #principal lunar
        M2 = 1.9324 #principal lunar
        return a * (numpy.cos(2*pi*O1*x + b)) + c * (numpy.cos(2*pi*M2*x + d))

    a = FitParam("O1 Amp", 0., -10., 10.)
    b = FitParam("O1 Shift", 0., -10., 10.,logscale="True")
    c = FitParam("M2 Amp", 0., -10., 10.)
    d = FitParam("M2 Shift", 0., -10., 10.,logscale="True")
    params = [a, b, c, d]
    values = guifit(x, y, fit, params, xlabel="Time (s)", ylabel="amplitude (ft)")
    return values

dl_O1_M2_fit = fitwin(t1, dl_O1_M2)
wl_O1_M2_fit = fitwin(t1, wl_O1_M2)

dl_fit = fitwin(t1,ddl)
wl_fit = fitwin(t1,dwl)


dlphs_O1 = dl_O1_M2_fit[1]
wlphs_O1 = wl_O1_M2_fit[1]
dlphs_M2 = dl_O1_M2_fit[3]
wlphs_M2 = wl_O1_M2_fit[3]
dlamp_O1 = dl_O1_M2_fit[0]
wlamp_O1 = wl_O1_M2_fit[0]
dlamp_M2 = dl_O1_M2_fit[2]
wlamp_M2 = wl_O1_M2_fit[2]

##non-gui regression - this has some issues
#def regfit(x,y):
#    def fit1(x,p):
#        #O1 = 0.9295 #principal lunar
#        #M2 = 1.9324 #principal lunar
#        return (p[0] * (numpy.cos(2*3.14159*0.9295*x + p[1])) + p[2] * (numpy.cos(2*3.14159*1.9324*x + p[3])))
#    def err(p,y,x):
#        return y - fit1(x,p)
#    p = [-10.0, -10.0, -10.0, -10.0]
#    results = op.leastsq(err,p,args=(y,x), xtol=1.49012e-10)
#    return results

#print regfit(t1,dl_O1_M2)

#calculate phase shift
phase_sft_O1 = wlphs_O1 - dlphs_O1
phase_sft_M2 = wlphs_M2 - dlphs_M2

delt_O1 = (phase_sft_O1/(O1*360))*24
delt_M2 = (phase_sft_M2/(M2*360))*24

#determine tidal potential Cutillo and Bredehoeft 2010 pg 5 eq 4
f_O1 = math.sin(float(lat[1])*pi/180)*math.cos(float(lat[1])*pi/180)
f_M2 = 0.5*math.cos(float(lat[1])*pi/180)**2

A2_M2 = g_ft*Km*b_M2*f_M2
A2_O1 = g_ft*Km*b_O1*f_O1

#Calculate ratio of head change to change in potential
dW2_M2 = A2_M2/(wlamp_M2)
dW2_O1 = A2_O1/(wlamp_O1)

#estimate specific storage Cutillo and Bredehoeft 2010
def SS(rat):
    return 6.95690250E-10*rat

Ss_M2 = SS(dW2_M2)
Ss_O1 = SS(dW2_O1)

def curv(Y,P,r):
    rc = (r/12.0)*(r/12.0)
    X = -1421.15/(0.215746 + Y) - 13.3401 - 0.000000143487*Y**4 - 9.58311E-16*Y**8*math.cos(0.9895 + Y + 1421.08/(0.215746 + Y) + 0.000000143487*Y**4)
    T = (X*rc)/P
    return T

Trans_M2 = curv(delt_M2,P_M2,r)
Trans_O1 = curv(delt_O1,P_O1,r)

tf=time.clock()
print '...Done!',tf-t0, 'seconds'
t0=time.clock

###########################################################################
# Calculate BP Response Function
###########################################################################
ti=time.clock() # measure time of calculation
print 'Calculating BP Response function...',
t0=time.clock()

# create lag matrix for regression
bpmat = tools.lagmat(dbp, lag, original='in')
etmat = tools.lagmat(ddl, lag, original='in')
#lamat combines lag matrices of bp and et
lamat = numpy.column_stack([bpmat,etmat])
#for i in range(len(etmat)):
#    lagmat.append(bpmat[i]+etmat[i])
#transpose matrix to determine required length
#run least squared regression
sqrd = numpy.linalg.lstsq(bpmat,dwl)
#determine lag coefficients of the lag matrix lamat
sqrdlag = numpy.linalg.lstsq(lamat,dwl)

wlls = sqrd[0]
#lagls return the coefficients of the least squares of lamat
lagls = sqrdlag[0]

cumls = numpy.cumsum(wlls)
#returns cumulative coefficients of et and bp (lamat)
lagcumls =numpy.cumsum(lagls)

ymod = numpy.dot(bpmat,wlls)
lagmod = numpy.dot(lamat,lagls)

#resid gives the residual of the bp
resid = [(dwl[i] - ymod[i])for i in range(len(dwl))]

#alpha returns the lag coefficients associated with bp
alpha = lagls[0:len(lagls)/2]
alpha_cum = numpy.cumsum(alpha)
#gamma returns the lag coefficients associated with ET
gamma = lagls[len(lagls)/2:len(lagls)]
gamma_cum = numpy.cumsum(gamma)

lag_time = []
for i in range(len(t1)):
    lag_time.append((t1[i] - t1[0])*24)


######################################### determine slope of late time data
lag_trim1 = lag_time[0:len(cumls)]
lag_time_trim = lag_trim1[len(lag_trim1)-(len(lag_trim1)/2):len(lag_trim1)]
alpha_trim = alpha_cum[len(lag_trim1)-(len(lag_trim1)/2):len(lag_trim1)]
#calculate slope of late-time data
lag_len = len(lag_time_trim)
tran = numpy.array([lag_time_trim, numpy.ones(lag_len)])

reg_late = numpy.linalg.lstsq(tran.T,alpha_trim)[0]
late_line=[]
for i in range(len(lag_trim1)):
    late_line.append(reg_late[0] * lag_trim1[i] + reg_late[1]) #regression line


######################################## determine slope of early time data
lag_time_trim2 = lag_trim1[0:len(lag_trim1)-int(round((len(lag_trim1)/1.5),0))]
alpha_trim2 = alpha_cum[0:len(lag_trim1)-int(round((len(lag_trim1)/1.5),0))]

lag_len1 = len(lag_time_trim2)
tran2 = numpy.array([lag_time_trim2, numpy.ones(lag_len1)])

reg_early = numpy.linalg.lstsq(tran2.T,alpha_trim2)[0]
early_line= []
for i in range(len(lag_trim1)):
    early_line.append(reg_early[0] * lag_trim1[i] + reg_early[1]) #regression line

aquifer_type = []
if reg_early[0] > 0.001:
    aquifer_type = 'borehole storage'
elif reg_early[0] < -0.001:
    aquifer_type = 'unconfined conditions'
else:
    aquifer_type = 'confined conditions'


tf=time.clock()
print '...Done!',tf-t0, 'seconds'
t0=time.clock

###########################################################################
# Make Plots
###########################################################################


fig_3 = well_name + ' filtered data O1'
fig_4 = well_name + ' filtered data M2'
fig_5 = well_name + ' correlations '

#multipage pdf figures
pp = PdfPages('fs'+os.path.splitext(wlfile)[0]+'.pdf')

#figure 1
fig_1 = well_name + ' bp response function'
plt.figure(fig_1)
plt.suptitle(fig_1, x= 0.2, y=.99, fontsize='small')
plt.subplot(2,1,1)
#plt.plot(lag_time[0:len(cumls)],cumls, label='b.p. alone')
plt.plot(lag_time[0:len(cumls)],alpha_cum,"o", label='b.p. when \n considering e.t.')
# plt.plot(lag_time[0:len(cumls)],gamma_cum, label='e.t.')
plt.plot(lag_trim1, late_line, 'r-', label='late reg.')
plt.plot(lag_trim1, early_line, 'g-', label='early reg.')
plt.xlabel('lag (hr)')
plt.ylabel('cumulative response function')
plt.legend(loc=4,fontsize='small')
plt.subplot(2,1,2)
plt.plot(lag_time, dwl, label='wl', lw=2)
plt.plot(lag_time, ymod, label='wl modeled w bp')
plt.plot(lag_time, lagmod, 'r--', label='wl modeled w bp&et')
plt.legend(loc=4, fontsize='small')
plt.xlim(0,lag)
plt.ylabel('change (ft)')
plt.xlabel('time (hrs)')
plt.tight_layout()
pp.savefig()
plt.close()

#figure 2
fig_2 = well_name + ' signal processing'
plt.figure(fig_2)
plt.suptitle(fig_2, x=0.2, fontsize='small')
plt.title(os.path.splitext(wlfile)[0])
plt.subplot(2,1,1)
plt.xcorr(dl_O1[1],wl_O1[1],maxlags=500)
plt.ylim(-1.1,1.1)
plt.tick_params(which='both',labelsize=8)
plt.xlabel('lag (min)',fontsize='small')
plt.ylabel('correl',fontsize='small')
plt.title('Cross Correl O1',fontsize='small')
plt.subplot(2,1,2)
plt.xcorr(dl_M2[1],wl_M2[1],maxlags=500)
plt.ylim(-1.1,1.1)
plt.tick_params(which='both',labelsize=8)
plt.xlabel('lag (min)',fontsize='small')
plt.ylabel('correl',fontsize='small')
plt.title('Cross Correl M2',fontsize='small')
plt.tight_layout()
pp.savefig()
plt.close()

##figure 3 - filtered data
#plt.figure(fig_3)
#plt.suptitle(fig_3, x=0.2, fontsize='small')
#plt.title(os.path.splitext(wlfile)[0])
#plt.plot(dl_O1, label="Grav. Tide")
#plt.plot(wl_O1, label="WL")
#plt.tick_params(labelsize=8)
#plt.xlabel('time (days)',fontsize='small')
#plt.ylabel('change (ft)',fontsize='small')
#plt.xlim(0,lag/2)
#plt.legend(loc=4,fontsize='small')
#plt.tight_layout()
#pp.savefig()
#plt.close()
#
##figure 4 - filtered data
#plt.figure(fig_4)
#plt.suptitle(fig_4, x=0.2, fontsize='small')
#plt.title(os.path.splitext(wlfile)[0])
#plt.plot(dl_M2, label="Grav. Tide")
#plt.plot(wl_M2, label="WL")
#plt.tick_params(labelsize=8)
#plt.xlabel('time (days)',fontsize='small')
#plt.ylabel('change (ft)',fontsize='small')
#plt.xlim(0,lag/2)
#plt.legend(loc=2,fontsize='small')
#plt.tight_layout()
#pp.savefig()
#plt.close()


#figure 5 -
plt.figure(fig_5)
plt.suptitle(fig_5, x=0.2, fontsize='small')
plt.title(os.path.splitext(wlfile)[0])
zfta = (scipy.fft(wl))
zffta = abs(zfta.real)
zftb = (fft.fftfreq(len(wl))*spd)
zfftb = abs(zftb.real)
plt.subplot(2,1,1)
plt.plot(zfftb,zffta)
plt.tick_params(labelsize=8)
plt.xlabel('frequency (cpd)',fontsize='small')
plt.ylabel('amplitude')
plt.title('WL fft',fontsize='small')
plt.xlim(0,4)
plt.ylim(0,30)
#plt.subplot(2,1,2)
#plt.plot(t1,wl, 'b')
#plt.tick_params(labelsize=8)
#plt.xlabel('julian days',fontsize='small')
#plt.ylabel('water level (ft)',fontsize='small')
#plt.twinx()
#plt.plot(t1,f3(LSQ_wl_O1[2],t1), 'r')
#plt.plot(t1,f4(LSQ_wl_M2[2],t1), 'g')
#plt.tick_params(labelsize=8)
#plt.xlim(0,20)
#plt.ylabel('tidal strain (ppb)',fontsize='small')
#plt.tick_params(labelsize=8)
#plt.tight_layout()
#plt.title('Regression Fit',fontsize='small')
pp.savefig()
plt.close()
pp.close()

###########################################################################
# Write output to files
###########################################################################

# create row of data for compiled output file info.csv
myCSVrow = [os.path.splitext(wlfile)[0],well_name, A2_O1, A2_M2, phase_sft_O1, phase_sft_M2, delt_O1,
            delt_M2, Trans_M2, Trans_O1, Ss_O1, Ss_M2, wlphs_O1, dlphs_O1, wlphs_M2, dlphs_M2,
            wlamp_O1, dlamp_O1, wlamp_M2, dlamp_M2, reg_late[1], reg_early[0], aquifer_type]
# add data row to compiled output file
compfile = open('info.csv', 'a')
writer = csv.writer(compfile)
writer.writerow(myCSVrow)
compfile.close()


#export tidal data to individual (well specific) output file
theoutfile=open(outfile,"wb")
filewriter = csv.writer(theoutfile, delimiter=',')
#write header
header = ['xl_time','date_time','V_ugal','vert_mm','areal_mm','WDD_tam','potential','dilation_ppb','wl_ft','dbp','dwl','resid','bp']
filewriter.writerow(header)
for row in range(0,1):
    for i in range(len(d1)):
    #you can add more columns here
        filewriter.writerow([wlt[i],d1[i],Grav_tide[i],vert[i],areal[i],WDD_tam[i],potential[i],
                             dl[i],wl[i],dbp[i],dwl[i],resid[i],bp[i]])
theoutfile.close()

##################    fin     #############################################