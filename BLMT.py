# -*- coding: utf-8 -*-
"""
Created on Thu Jan 09 11:31:08 2014

@author: paulinkenbrandt
"""

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
import numpy as np
import scipy
import scipy.signal as scg
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
import xlrd
import pandas as pd
import scipy.optimize as op

warnings.simplefilter("ignore", np.ComplexWarning)

###########################################################################
"""
INPUT FILES ARE PUT IN BELOW

"""

p = 7.692E5

lag = 100 #this lag is in reference to the barometric efficiency function
tol = 0.008  #percentage of variance in frequency allowed; default is 2%
r = 5 #well radius in inches
Be = 0.10 #barometric efficiency
numb = 5000 # number of values to process
spd = 24*4 #samples per day hourly sampling = 24
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
ti=time.clock() # measure time of calcudt = pd.date_range(pd.datetime(wldt[6][0],wldt[6][1],wldt[6][2],wldt[6][3]),pd.datetime(wldt[-6][0],wldt[-6][1],wldt[-6][2],wldt[-6][3]),freq='15Min')lation
print 'Loading file...',
t0=time.clock()

wlfile='BLMT.xlsx'
xls_wrkbk = xlrd.open_workbook("BLMT.xlsx")
wl_sht = xls_wrkbk.sheet_by_name("090625")



ta = np.array([float((wl_sht.cell(i,1).value)) for i in range(1, wl_sht.nrows)])[4300:8396]
tb = np.array([float((wl_sht.cell(i,2).value)) for i in range(1, wl_sht.nrows)])[4300:8396] 
tc = np.array([float((wl_sht.cell(i,3).value)) for i in range(1, wl_sht.nrows)])[4300:8396]
td = np.array([float((wl_sht.cell(i,4).value)) for i in range(1, wl_sht.nrows)])[4300:8396]
te = np.array([float((wl_sht.cell(i,5).value)) for i in range(1, wl_sht.nrows)])[4300:8396]
tf = np.array([float((wl_sht.cell(i,6).value)) for i in range(1, wl_sht.nrows)])[4300:8396]
tg = np.array([float((wl_sht.cell(i,7).value)) for i in range(1, wl_sht.nrows)])[4300:8396]
th = np.array([float((wl_sht.cell(i,8).value)) for i in range(1, wl_sht.nrows)])[4300:8396]


wldt = [xlrd.xldate_as_tuple(wl_sht.cell(i,0).value, xls_wrkbk.datemode) for i in range(1, wl_sht.nrows)][4300:8396]



outfile = "c" + os.path.splitext(wlfile)[0] + ".csv"

#wlfiler = csv.reader(open(wlfile, 'rb'), delimiter=",")
#dy, u, l, nm, w1, t, vert = [], [], [], [], [], [], []

#remove existing figure files
if os.path.isfile('fs'+os.path.splitext(wlfile)[0]+'.pdf'):
    os.remove('fs'+os.path.splitext(wlfile)[0]+'.pdf')
else:
    print "No old file!"


#pick well name, lat., long., and elevation data out of header of wl file
well_name = "BLM-1" #u[0][1]
lon = -116.47136
lat = 36.40813
elv = round(float(7415)/3.2808,3)
gmtt = -8

tff=time.clock()
print '...Done!',round(tff-t0,2), 'seconds'
t0=time.clock

##############################################################################
# prepare time variables for tidal function
##############################################################################
ti=time.clock() # measure time of calculation
print 'Making time...',
t0=time.clock()


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
    return XLS



## create a list of excel dates
wlt = [(calc_jday(wldt[i][0],wldt[i][1],wldt[i][2],wldt[i][3],wldt[i][4],wldt[i][5])) for i in range(len(wldt))]


tff=time.clock()
print '...Done!',round(tff-t0,2), 'seconds'
t0=time.clock

##############################################################################
# run tidal function
##############################################################################

ti=time.clock() # measure time of calculation
print 'Calling Tamura Code...',
t0=time.clock()

#iterate tamura code over each measurement
#t = [tamura.tide(wldt[i][0], wldt[i][1], wldt[i][2], wldt[i][3], wldt[i][4], wldt[i][5], lon, lat, elv, 0, gmtt) for i in range(len(wldt))]
#
#
#arl = np.array([(t[i]*p*1E-5) for i in range(len(t))])                            # areal determine areal strain from Agnew 2007, units in mm
#potential = np.array([(-318.49681664*t[i] - 0.50889238) for i in range(len(t))])
#wdd = np.array([(t[i]*(0.99362956469)-7.8749754) for i in range(len(t))])       # WDD is used to recreate output from TSoft
#dl = np.array([(0.381611837 * t[i] - 0.000609517) for i in range(len(t))])     # dilation from relationship defined using Harrison's code
#vert = np.array([(t[i] * 1.692) for i in range(len(t))])                            # determine vertical strain from Agnew 2007; units are in sec squared, meaning results in mm
#grv = np.array([(-1*t[i]) for i in range(len(t))])

tff=time.clock()
print '...Done!',round(tff-t0,2), 'seconds'
t0=time.clock

##############################################################################
#  standardize and densify  data
##############################################################################

ti=time.clock() # measure time of calculation
print 'Standardizing Data...',
t0=time.clock()


t1 = np.linspace(wlt[0], wlt[-1], len(wlt))  # sets size and interval of time


def stdnz(A):
    '''this function standardizes data by subtracting the mean and dividing by std dev'''
    A = [(A[i] - np.mean(A))/np.std(A) for i in range(len(A))]
    return A

def dens(y,x,mult):
    '''this function resamples data at a high rate
    \n y = data
    \n x = time
    \n mult = multiple to increase sampling by'''
    ys = y[len(y)/50:len(y)/8] #shortens data to ease calculation
    xs = x[len(y)/50:len(y)/8]
    new_length = len(xs)*mult
    xexten = np.linspace(xs.min(), xs.max(), new_length)
    yexten = scipy.interpolate.interp1d(xs,ys, kind='cubic')(xexten)
    return xexten, yexten

def chn(A):
    '''this function provides user with differences between consecutive values'''
    A = [(A[i] - A[i+1]) for i in range(len(A)-1)]
    A.append(0.0)
    return np.array(A)

stta = stdnz(ta) #standardized wl
sttb = stdnz(tb)
sttc = stdnz(tc)
sttd = stdnz(td)
stte = stdnz(te)
sttf = stdnz(tf)
sttg = stdnz(tg)
stth = stdnz(th)

#stdl = stdnz(arl) #standardized earth tide dilation

# these are change in consecutive standardized values
dta = chn(stta)
dtb = chn(sttb)
dtc = chn(sttc)
dtd = chn(sttd)
dte = chn(stte)
dtf = chn(sttf)
dtg = chn(sttg)
dth = chn(stth)

#ddl = chn(stdl)

##densified resampled data
#dnwl = dens(dwl,t1,60)
#dnbp = dens(dbp,t1,60)
#dndl = dens(ddl,t1,60)

tff=time.clock()
print '...Done!',round(tff-t0,2), 'seconds'
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
    #ftc = fft.fftshift(fta)
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
    ftc = fft.fftshift(fta)
    rl = ftc.real
    im = ftc.imag
    mag = [math.sqrt(rl[i]**2 + im[i]**2) for i in range(len(rl))]
    phase = [math.atan2(im[i],rl[i]) for i in range(len(rl))]
    return mag, phase

#dlmg = phasefind(dl)[0]
tamg = phasefind(ta)[0]
tbmg = phasefind(tb)[0]
tcmg = phasefind(tc)[0]
tdmg = phasefind(td)[0]
temg = phasefind(te)[0]
tfmg = phasefind(tf)[0]
tgmg = phasefind(tg)[0]
thmg = phasefind(th)[0]

#dlph = phasefind(dl)[1]
taph = phasefind(ta)[1]
tbph = phasefind(tb)[1]
tcph = phasefind(tc)[1]
tdph = phasefind(td)[1]
teph = phasefind(te)[1]
tfph = phasefind(tf)[1]
tgph = phasefind(tg)[1]
thph = phasefind(th)[1]



#filter tidal data
ta_O1 = filt(O1,tol,ta,spd)
tb_O1 = filt(O1,tol,tb,spd)
tc_O1 = filt(O1,tol,tc,spd)
td_O1 = filt(O1,tol,td,spd)
te_O1 = filt(O1,tol,te,spd)
tf_O1 = filt(O1,tol,tf,spd)
tg_O1 = filt(O1,tol,tg,spd)
th_O1 = filt(O1,tol,th,spd)

ta_M2 = filt(M2,tol,ta,spd)
tb_M2 = filt(M2,tol,tb,spd)
tc_M2 = filt(M2,tol,tc,spd)
td_M2 = filt(M2,tol,td,spd)
te_M2 = filt(M2,tol,te,spd)
tf_M2 = filt(M2,tol,tf,spd)
tg_M2 = filt(M2,tol,tg,spd)
th_M2 = filt(M2,tol,th,spd)

tab_ph = [ta_O1[4][i] - tb_O1[4][i] for i in range(len(ta_O1))]
tae_ph = [ta_O1[4][i] - te_O1[4][i] for i in range(len(ta_O1))]
print tab_ph
print tae_ph
##combine filtered signals
ta_O1_M2 = np.array(map(operator.add, ta_O1[0], ta_M2[0]))
tb_O1_M2 = np.array(map(operator.add, tb_O1[0], tb_M2[0]))
tc_O1_M2 = np.array(map(operator.add, tc_O1[0], tc_M2[0]))
td_O1_M2 = np.array(map(operator.add, td_O1[0], td_M2[0]))
te_O1_M2 = np.array(map(operator.add, te_O1[0], te_M2[0]))
tf_O1_M2 = np.array(map(operator.add, tf_O1[0], tf_M2[0]))
tg_O1_M2 = np.array(map(operator.add, tg_O1[0], tg_M2[0]))
th_O1_M2 = np.array(map(operator.add, th_O1[0], th_M2[0]))

tff=time.clock()
print '...Done!',round(tff-t0,2), 'seconds'
t0=time.clock

##########################################################################
# Cross Corr
###########################################################################
tatb = scg.correlate(ta[200:1200],te[200:1200],mode="valid")

print tatb
ind = []
for i in range(1,len(tatb)-1):
    if  abs(tatb[i])>abs(tatb[i-1]) and abs(tatb[i])<abs(tatb[i+1]):
        ind.append(i)

print ind
print len(tatb)
print len(ta)


##########################################################################
# Regression Analysis
###########################################################################
ti=time.clock() # measure time of calculation
print 'Regression analsyses...',
t0=time.clock()

def regO1(x,y):
    '''this regression is for O1'''
    def fitO1(x,p):
        return (p[0] + p[1]*np.cos(2*3.14159*0.9295*x) + p[2] * np.sin(2*3.14159*0.9295*x))
    def errO1(p,y,x):
        return y - fitO1(x,p)
    p = [-1.0, -1.0, -1.0]
    rst = op.leastsq(errO1,p,args=(y,x))[0]
    ak = math.sqrt(rst[1]**2+rst[2]**2)
    phi = np.arctan2(rst[1],rst[2])*(180/3.14159)*-2  #phase in min
    return  rst, ak, phi

def fitO1(x,p):
    return (p[0] + p[1]*np.cos(2*3.14159*0.9295*x) + p[2] * np.sin(2*3.14159*0.9295*x))

def regM2(x,y):
    '''this regression is for M2'''
    def fitM2(x,p):
        return (p[0] + p[1]*np.cos(2*3.14159*1.9324*x)+ p[2] * np.sin(2*3.14159*1.9324*x))
    def errM2(p,y,x):
        return y - fitM2(x,p)
    p = [-1.0, -1.0, -1.0]
    rst = op.leastsq(errM2,p,args=(y,x))[0]
    ak = math.sqrt(rst[1]**2+rst[2]**2)
    phi = np.arctan2(rst[1],rst[2])*(180/3.14159)*-2 #phase in min
    return  rst, ak, phi
def fitM2(x,p):
    return (p[0] + p[1]*np.cos(2*3.14159*1.9324*x)+ p[2] * np.sin(2*3.14159*1.9324*x))

def regO1M2(x,y):
    def fitO1M2(x,p):
        return (p[0]+p[1]*np.cos(2*3.14159*0.9295*(x+p[2]))+p[3]*np.cos(2*3.14159*1.9324*(x+p[2])))
    def errO1M2(p,y,x):
        return y - fitO1M2(x,p)
    p = [0.0,-5.0,-5.0,-5.0]
    rst = op.leastsq(errO1M2,p,args=(y,x))[0]
    return rst

def fitO1M2(x,p):
    return (p[0]+p[1]*np.cos(2*3.14159*0.9295*(x+p[2]))+p[3]*np.cos(2*3.14159*1.9324*(x+p[2])))

taphs_O1M2 = regO1M2(t1,ta)[2]
tbphs_O1M2 = regO1M2(t1,tb)[2]
tcphs_O1M2 = regO1M2(t1,tc)[2]
tdphs_O1M2 = regO1M2(t1,td)[2]
tephs_O1M2 = regO1M2(t1,te)[2]
tfphs_O1M2 = regO1M2(t1,tf)[2]
tgphs_O1M2 = regO1M2(t1,tg)[2]
thphs_O1M2 = regO1M2(t1,th)[2]
#print regO1M2(t1,dl)

#dlphs_O1 = regO1(t1,dl)[2]
taphs_O1 = regO1(t1,ta)[2]
tbphs_O1 = regO1(t1,tb)[2]
tcphs_O1 = regO1(t1,tc)[2]
tdphs_O1 = regO1(t1,td)[2]
tephs_O1 = regO1(t1,te)[2]
tfphs_O1 = regO1(t1,tf)[2]
tgphs_O1 = regO1(t1,tg)[2]
thphs_O1 = regO1(t1,th)[2]

#dlphs_M2 = regM2(t1,dl)[2]
taphs_M2 = regM2(t1,ta)[2]
tbphs_M2 = regM2(t1,tb)[2]
tcphs_M2 = regM2(t1,tc)[2]
tdphs_M2 = regM2(t1,td)[2]
tephs_M2 = regM2(t1,te)[2]
tfphs_M2 = regM2(t1,tf)[2]
tgphs_M2 = regM2(t1,tg)[2]
thphs_M2 = regM2(t1,th)[2]

#dlamp_O1 = regO1(t1,dl)[1]
taamp_O1 = regO1(t1,ta)[1]
tbamp_O1 = regO1(t1,tb)[1]
tcamp_O1 = regO1(t1,tc)[1]
tdamp_O1 = regO1(t1,td)[1]
teamp_O1 = regO1(t1,te)[1]
tfamp_O1 = regO1(t1,tf)[1]
tgamp_O1 = regO1(t1,tg)[1]
thamp_O1 = regO1(t1,th)[1]

#dlamp_M2 = regM2(t1,dl)[1]
taamp_M2 = regM2(t1,ta)[1]
tbamp_M2 = regM2(t1,tb)[1]
tcamp_M2 = regM2(t1,tc)[1]
tdamp_M2 = regM2(t1,td)[1]
teamp_M2 = regM2(t1,te)[1]
tfamp_M2 = regM2(t1,tf)[1]
tgamp_M2 = regM2(t1,tg)[1]
thamp_M2 = regM2(t1,th)[1]


#calculate phase shift
phs_ab_O1 = taphs_O1 - tbphs_O1
phs_ac_O1 = taphs_O1 - tcphs_O1
phs_ad_O1 = taphs_O1 - tdphs_O1
phs_ae_O1 = taphs_O1 - tephs_O1
phs_af_O1 = taphs_O1 - tfphs_O1
phs_ag_O1 = taphs_O1 - tgphs_O1
phs_ah_O1 = taphs_O1 - thphs_O1

phs_ab_M2 = taphs_M2 - tbphs_M2
phs_ac_M2 = taphs_M2 - tcphs_M2
phs_ad_M2 = taphs_M2 - tdphs_M2
phs_ae_M2 = taphs_M2 - tephs_M2
phs_af_M2 = taphs_M2 - tfphs_M2
phs_ag_M2 = taphs_M2 - tgphs_M2
phs_ah_M2 = taphs_M2 - thphs_M2

phs_ab_O1M2 = taphs_O1M2 - tbphs_O1M2
phs_ac_O1M2 = taphs_O1M2 - tcphs_O1M2
phs_ad_O1M2 = taphs_O1M2 - tdphs_O1M2
phs_ae_O1M2 = taphs_O1M2 - tephs_O1M2
phs_af_O1M2 = taphs_O1M2 - tfphs_O1M2
phs_ag_O1M2 = taphs_O1M2 - tgphs_O1M2
phs_ah_O1M2 = taphs_O1M2 - thphs_O1M2



tff=time.clock()
print '...Done!',round(tff-t0,2), 'seconds'
t0=time.clock


###########################################################################
# Make Plots
###########################################################################


fig_3 = well_name + ' filtered data O1'
fig_4 = well_name + ' filtered data M2'
fig_5 = well_name + ' correlations '

#multipage pdf figures
pp = PdfPages('fs'+os.path.splitext(wlfile)[0]+'.pdf')


#figure 2
fig_2 = well_name + ' TA-TB'
plt.xkcd()
plt.figure(fig_2)
plt.suptitle(fig_2, x=0.2, fontsize='small')
plt.title(os.path.splitext(wlfile)[0])
plt.subplot(2,1,1)
plt.xcorr(ta_O1[1],tb_O1[1],maxlags=20)
plt.ylim(-1.1,1.1)
plt.tick_params(which='both',labelsize=8)
plt.xlabel('lag (hrs)',fontsize='small')
plt.ylabel('correl',fontsize='small')
plt.title('Cross Correl O1',fontsize='small')
plt.subplot(2,1,2)
plt.xcorr(ta_M2[1],tb_M2[1],maxlags=20)
plt.ylim(-1.1,1.1)
plt.tick_params(which='both',labelsize=8)
plt.xlabel('lag (hrs)',fontsize='small')
plt.ylabel('correl',fontsize='small')
plt.title('Cross Correl M2',fontsize='small')
plt.tight_layout()
pp.savefig()
plt.close()

#figure 2
fig_3 = well_name + ' TA-TE'
plt.figure(fig_3)
plt.suptitle(fig_3, x=0.2, fontsize='small')
plt.title(os.path.splitext(wlfile)[0])
plt.subplot(2,1,1)
plt.xcorr(ta_O1[1],te_O1[1],maxlags=20)
plt.ylim(-1.1,1.1)
plt.tick_params(which='both',labelsize=8)
plt.xlabel('lag (hrs)',fontsize='small')
plt.ylabel('correl',fontsize='small')
plt.title('Cross Correl O1',fontsize='small')
plt.subplot(2,1,2)
plt.xcorr(ta_M2[1],te_M2[1],maxlags=20)
plt.ylim(-1.1,1.1)
plt.tick_params(which='both',labelsize=8)
plt.xlabel('lag (hrs)',fontsize='small')
plt.ylabel('correl',fontsize='small')
plt.title('Cross Correl M2',fontsize='small')
plt.tight_layout()
pp.savefig()
plt.close()

#figure 5 -
fig_5 = well_name + ' correlations '
plt.figure(fig_5)
plt.suptitle(fig_5, x=0.2, fontsize='small')
plt.title(os.path.splitext(wlfile)[0])
zfta = (scipy.fft(ta))
zffta = abs(zfta.real)
zftb = (fft.fftfreq(len(ta))*spd)
zfftb = abs(zftb.real)

plt.subplot(2,1,1)
plt.plot(zfftb,zffta)
plt.tick_params(labelsize=8)
plt.xlabel('frequency (cpd)',fontsize='small')
plt.ylabel('amplitude')
plt.xlim(0,10.0)
plt.title('WL fft',fontsize='small')

plt.subplot(2,1,2)
plt.plot(t1[500:1500],dta[500:1500], 'b')
plt.tick_params(labelsize=8)
plt.xlabel('julian days',fontsize='small')
plt.ylabel('water level (ft)',fontsize='small')
plt.twinx()
plt.plot(t1[500:1500],fitO1(t1,regO1(t1,dta)[0])[500:1500], 'r')
plt.plot(t1[500:1500],fitM2(t1,regM2(t1,dta)[0])[500:1500], 'g')
plt.plot(t1[500:1500],fitO1M2(t1,regO1M2(t1,dta))[500:1500], 'r--')
plt.tick_params(labelsize=8)
plt.ylabel('tidal strain (ppb)',fontsize='small')
plt.tick_params(labelsize=8)
plt.tight_layout()
plt.title('Regression Fit',fontsize='small')
pp.savefig()
plt.close()
pp.close()


###########################################################################
# Write output to files
###########################################################################

# create row of data for compiled output file info.csv
myCSVrow = [phs_ab_O1, phs_ac_O1, phs_ac_O1, phs_ad_O1, phs_ae_O1,
            phs_af_O1, phs_ag_O1, phs_ah_O1, phs_ab_M2, phs_ac_M2, phs_ad_M2, phs_ae_M2, phs_af_M2, phs_ag_M2,
            phs_ah_M2, taamp_O1, tbamp_O1, tgamp_O1, thamp_O1, taamp_M2, tbamp_M2, tgamp_M2, thamp_M2, phs_ab_O1M2, phs_ac_O1M2, phs_ad_O1M2, 
            phs_ae_O1M2, phs_af_O1M2, phs_ag_O1M2, phs_ah_O1M2 ]
# add data row to compiled output file
compfile = open('info2.csv', 'a')
writer = csv.writer(compfile)
writer.writerow(myCSVrow)
compfile.close()


##################    fin     #############################################
