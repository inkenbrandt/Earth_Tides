# -*- coding: utf-8 -*-
"""
Created on Thu Aug 15 14:17:49 2013

@author: paulinkenbrandt
"""

import csv
from itertools import islice
import os
import time
import sys
import math
import numpy, scipy
from scipy import fftpack, signal
import scipy.optimize as optimization
import matplotlib.pyplot as plt
import numpy.fft as fft
import statsmodels.tsa.tsatools as tools
import statsmodels.tsa.arima_process as arima
import cmath
from operator import itemgetter


sys.path.append('C:\\PROJECTS\\Snake_Valley\\PYTHON\\PROCESSING\\New folder')
import tamura


def skip_first(seq, n):
    #this function is to skip the header rows in the input files
    for i,item in enumerate(seq):
        if i >= n:
            yield item

def tideproc(inpfile,bpdata,edata):

    delta = 1.1562
    p = 7.692E5

    ###########################################################################
    """
    INPUT FILES ARE PUT IN BELOW
    """

    lag = 100
    tol = 0.05  #percentage of variance in frequency allowed; default is 2%
    r = 1 #well radius in inches
    Be = 0.10 #barometric efficiency
    numb = 2000 # number of values to process
    spd = 24 #samples per day hourly sampling = 24
    lagt = -6.0 #hours different from UTC (negative indicates west); UT is -7

    """
    INPUT FILES END HERE
    """
    ###########################################################################

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

    impfile = inpfile
    outfile = 'c'+impfile
    data = csv.reader(open(impfile, 'rb'), delimiter=",")
    dy, u, l, nm, d, wl, t, vert =[], [], [], [], [], [], [], []
    yrdty, year, month, day, hours, minutes, seconds, julday = [], [], [], [], [], [], [], []
    yrdty2,year2, month2, day2, hours2, minutes2, seconds2, julday2 = [], [], [], [], [], [], [], []
    yrdty3,year3, month3, day3, hours3, minutes3, seconds3, julday3 = [], [], [], [], [], [], [], []

    # read in bp data
    bpdata = bpdata
    bdata = csv.reader(open(bpdata, 'rb'), delimiter=",")
    v, d2, bp=[], [], []
    d3, SG33WDD, PW19S2, PW19M2, MXSWDD = [],[],[],[],[]

    etdata = edata

    #assign data in csv to arrays
    for row in data:
        u.append(row)

    for row in bdata:
        v.append(row)

    #pick well name, lat., long., and elevation data out of header of wl file
    well_name = u[0][1]
    lon = [float(u[5][1])]
    latt = [round(float(u[4][1]),3)]
    el = [round(float(u[10][1])/3.2808,3)]

    #import the bp data
    with open(bpdata, 'rb') as tot:
        csvreader1 = csv.reader(tot)
        for row in skip_first(csvreader1, 3):
            d2.append(row[2])
            bp.append(float(row[3]))

    #import the wl data
    with open(impfile, 'rb') as total:
        csvreader = csv.reader(total)
        for row in skip_first(csvreader, 62):
            dy.append(row[0])
            nm.append(row[1])

    #import supplemental earth tide data
    with open(etdata, 'rb') as tos:
        csvreader2 = csv.reader(tos)
        for row in skip_first(csvreader2,2):
            d3.append(row[5])
            SG33WDD.append(float(row[6]))
            PW19S2.append(row[7])
            PW19M2.append(row[8])
            MXSWDD.append(row[9])

    #import a smaller part of the wl data
    for i in range(len(dy)-numb,len(dy)):
        d.append(dy[i])
        wl.append(nm[i])

    #fill in last line of wl data
    wl[-1]=wl[-2]
    for i in range(len(wl)):
        if wl[i] is '':
            wl[i]=wl[i-1]

    #create a list of latitude, longitude, elevation, and gmt for tidal calculation
    lat = latt*len(d)
    longit = lon*len(d)
    elev = el*len(d)
    gmtt = [float(lagt)]*len(d)

    # define the various components of the date, represented by d
    # dates for wl data
    for i in range(len(d)):
        yrdty.append(time.strptime(d[i],"%Y-%m-%d %H:%M:%S"))
        year.append(int(yrdty[i].tm_year))
        month.append(int(yrdty[i].tm_mon))
        day.append(int(yrdty[i].tm_mday))
        hours.append(int(yrdty[i].tm_hour))
        minutes.append(int(yrdty[i].tm_min))
        seconds.append(int(0)) #yrdty[i].tm_sec
    # dates for bp data
    for i in range(len(d2)):
        yrdty2.append(time.strptime(d2[i],"%Y-%m-%d %H:%M:%S"))
        year2.append(int(yrdty2[i].tm_year))
        month2.append(int(yrdty2[i].tm_mon))
        day2.append(int(yrdty2[i].tm_mday))
        hours2.append(int(yrdty2[i].tm_hour))
        minutes2.append(int(yrdty2[i].tm_min))
        seconds2.append(int(0)) #yrdty2[i].tm_sec
    # dates for bp data
    for i in range(len(d3)):
        yrdty3.append(time.strptime(d3[i],"%m/%d/%Y %H:%M"))
        year3.append(int(yrdty3[i].tm_year))
        month3.append(int(yrdty3[i].tm_mon))
        day3.append(int(yrdty3[i].tm_mday))
        hours3.append(int(yrdty3[i].tm_hour))
        minutes3.append(int(yrdty3[i].tm_min))
        seconds3.append(int(0)) #yrdty2[i].tm_sec

    #julian day calculation
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
      return JD

    # create a list of julian dates
    for i in range(len(d)):
        julday.append(calc_jday(year[i],month[i],day[i],hours[i],minutes[i],seconds[i]))

    for i in range(len(d2)):
        julday2.append(calc_jday(year2[i],month2[i],day2[i],hours2[i],minutes2[i],seconds2[i]))

    for i in range(len(d3)):
        julday3.append(calc_jday(year3[i],month3[i],day3[i],hours3[i],minutes3[i],seconds3[i]))

    #run tidal function
    for i in range(len(d)):
        t.append(tamura.tide(int(year[i]), int(month[i]), int(day[i]), int(hours[i]), int(minutes[i]), int(seconds[i]), float(longit[i]), float(lat[i]), float(elev[i]), 0.0, lagt)) #float(gmtt[i])

    vert, Grav_tide, WDD_tam, areal, potential, dilation = [], [], [], [], [], []

    #determine vertical strain from Agnew 2007
    #units are in sec squared, meaning results in mm
    # areal determine areal strain from Agnew 2007, units in mm
    #dilation from relationship defined using Harrison's code
    #WDD is used to recreate output from TSoft
    for i in range(len(t)):
        areal.append(t[i]*p*1E-5)
        potential.append(-318.49681664*t[i] - 0.50889238)
        WDD_tam.append(t[i]*(-.99362956469)-7.8749754)
        dilation.append(0.381611837*t[i] - 0.000609517)
        vert.append(t[i] * 1.692)
        Grav_tide.append(-1*t[i])

    #convert to excel date-time numeric format
    xls_date = []
    for i in range(len(d)):
        xls_date.append(float(julday[i])-2415018.5)

    xls_date2 = []
    for i in range(len(d2)):
        xls_date2.append(float(julday2[i])-2415018.5)

    xls_date3 = []
    for i in range(len(d3)):
        xls_date3.append(float(julday3[i])-2415018.5)

    t_start = xls_date[0]
    t_end = xls_date[-1]
    t_len = (len(xls_date))

    #align bp data with wl data
    t1 = numpy.linspace(t_start, t_end, t_len)
    bpint = numpy.interp(t1, xls_date2, bp)
    etint = numpy.interp(t1, xls_date3, SG33WDD)

    xprep, yprep, zprep = [], [], []
    #convert text from csv to float values
    for i in range(len(julday)):
        xprep.append(float(julday[i]))
        yprep.append(float(dilation[i]))
        zprep.append(float(wl[i]))

    #put data into numpy arrays for analysis
    xdata = numpy.array(xprep)
    ydata = numpy.array(yprep)
    zdata = numpy.array(zprep)
    bpdata = numpy.array(bpint)
    etdata = numpy.array(etint)
    bp = bpdata
    z = zdata
    y = ydata
    #    tempdata = numpy.array(tempint)
    #standarize julian day to start at zero

    x0data = xdata - xdata[0]

    wl_z = []
    mn = numpy.mean(z)
    std = numpy.std(z)
    for i in range(len(z)):
        wl_z.append((z[i]-mn)/std)

    bp_z = []
    mn = numpy.mean(bp)
    std = numpy.std(bp)
    for i in range(len(bp)):
        bp_z.append((bp[i]-mn)/std)

    t_z = []
    mn = numpy.mean(y)
    std = numpy.std(y)
    for i in range(len(y)):
        t_z.append((t[i]-mn)/std)

    dbp = []
    for i in range(len(bp)-1):
        dbp.append(bp[i]-bp[i+1])

    dwl = []
    for i in range(len(z)-1):
        dwl.append(z[i]-z[i+1])

    dt = []
    for i in range(len(y)-1):
        dt.append(y[i]-y[i+1])

    dbp.append(0)

    dwl.append(0)

    dt.append(0)


    ###########################################################################
    #
    ############################################################ Filter Signals
    #
    ###########################################################################
    ''' these filtered data are not necessary,
    but are good for graphical comparison '''
    ### define filtering function
    def filt(frq,tol,data):
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
        crve = fft.ifft(bp2)
        yfilt = crve.real
        return yfilt



    #filter tidal data
    yfilt_O1 = filt(O1,tol,ydata)
    yfilt_M2 = filt(M2,tol,ydata)
    #filter wl data
    zfilt_O1 = filt(O1,tol,zdata)
    zfilt_M2 = filt(M2,tol,zdata)

    zffta = abs(fft.fft(zdata))
    zfftb = abs(fft.fftfreq(len(zdata))*spd)



    def phasefind(A,frq):
        spectrum = fft.fft(A)
        freq = fft.fftfreq(len(spectrum))
        r = []
        #filter = eliminate all values in the wl data fft except the frequencies in the range of interest
        for i in range(len(freq)):
            #spd is samples per day (if hourly = 24)
            if (freq[i]*spd)>(frq-frq*tol) and (freq[i]*spd)<(frq+frq*tol):
                r.append(freq[i]*spd)
            else:
                r.append(0)
        #find the place of the max complex value for the filtered frequencies and return the complex number
        p = max(enumerate(r), key=itemgetter(1))[0]
        pla = spectrum[p]
        T5 = cmath.phase(pla)*180/pi
        return T5

    yphsO1 = phasefind(ydata,O1)
    zphsO1 = phasefind(zdata,O1)
    phsO1 = zphsO1 - yphsO1
    yphsM2 = phasefind(ydata,M2)
    zphsM2 = phasefind(zdata,M2)
    phsM2 = zphsM2 - yphsM2


#    def phase_find(A,B,P):
#        period = P
#        tmax = len(xdata)*24
#        nsamples = len(A)
#        # calculate cross correlation of the two signals
#        t6 = numpy.linspace(0.0, tmax, nsamples, endpoint=False)
#        xcorr = numpy.correlate(A, B)
#        # The peak of the cross-correlation gives the shift between the two signals
#        # The xcorr array goes from -nsamples to nsamples
#        dt6 = numpy.linspace(-t6[-1], t6[-1], 2*nsamples-1)
#        recovered_time_shift = dt6[xcorr.argmax()]
#
#        # force the phase shift to be in [-pi:pi]
#        #recovered_phase_shift = 2*pi*(((0.5 + recovered_time_shift/(period*24)) % 1.0) - 0.5)
#        return recovered_time_shift
#
#
#    O1_ph= phase_find(ydata,zdata,P_O1)
#    M2_ph= phase_find(ydata,zdata,P_M2)




    ###########################################################################
    #
    ####################################################### Regression Analysis
    #
    ###########################################################################

    #define functions used for least squares fitting
    def f3(p, x):
        #a,b,c = p
        m = 2.0 * O1 * pi
        y = p[0] + p[1] * (numpy.cos(m*x)) + p[2] * (numpy.sin(m*x))
        return y

    def f4(p, x):
        #a,b,c = p
        m =2.0 * M2 * pi
        y  = p[0] + p[1] * (numpy.cos(m*x)) + p[2] * (numpy.sin(m*x))
        return y

    #define functions to minimize
    def err3(p,y,x):
        return y - f3(p,x)

    def err4(p,y,x):
        return y - f4(p,x)

    #conducts regression, then calculates amplitude and phase angle
    def lstsq(func,y,x):
        #define starting values with x0
       x0 = numpy.array([sum(y)/float(len(y)), 0.01, 0.01])
       fit ,chks = optimization.leastsq(func, x0, args=(y, x))
       amp = math.sqrt((fit[1]**2)+(fit[2]**2))      #amplitude
       phi = numpy.arctan(-1*(fit[2],fit[1]))*(180/pi)   #phase angle
       return amp,phi,fit

    #water level signal regression
    WLO1 = lstsq(err3,zdata,xdata)
    WLM2 = lstsq(err4,zdata,xdata)

    #tide signal regression
    TdO1 = lstsq(err3,ydata,xdata)
    TdM2 = lstsq(err4,ydata,xdata)

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
    dW2_M2 = A2_M2/(WLM2[0])
    dW2_O1 = A2_O1/(WLO1[0])

    #estimate specific storage Cutillo and Bredehoeft 2010
    def SS(rat):
        return 6.95690250E-10*rat

    Ss_M2 = SS(dW2_M2)
    Ss_O1 = SS(dW2_O1)

    def curv(Y,P,r):
        rc = (r/12.0)*(r/12.0)
        Y = Y
        X = -1421.15/(0.215746 + Y) - 13.3401 - 0.000000143487*Y**4 - 9.58311E-16*Y**8*math.cos(0.9895 + Y + 1421.08/(0.215746 + Y) + 0.000000143487*Y**4)
        T = (X*rc)/P
        return T

    Trans_M2 = curv(phase_sft_O1,P_M2,r)
    Trans_O1 = curv(phase_sft_M2,P_O1,r)


    ###########################################################################
    #
    ############################################ Calculate BP Response Function
    #
    ###########################################################################

    # create lag matrix for regression
    bpmat = tools.lagmat(dbp, lag, original='in')
    etmat = tools.lagmat(dt, lag, original='in')
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
    resid=[]
    for i in range(len(dwl)):
        resid.append(dwl[i] - ymod[i])
    #alpha returns the lag coefficients associated with bp
    alpha = lagls[0:len(lagls)/2]
    alpha_cum = numpy.cumsum(alpha)
    #gamma returns the lag coefficients associated with ET
    gamma = lagls[len(lagls)/2:len(lagls)]
    gamma_cum = numpy.cumsum(gamma)

    lag_time = []
    for i in range(len(xls_date)):
        lag_time.append((xls_date[i] - xls_date[0])*24)


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


    ###########################################################################
    #
    ################################################################ Make Plots
    #
    ###########################################################################
    fig_1_lab = well_name + ' bp response function'
    fig_2_lab = well_name + ' signal processing'

    plt.figure(fig_1_lab)
    plt.suptitle(fig_1_lab, x= 0.2, y=.99, fontsize='small')
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
    plt.plot(lag_time,dwl, label='wl', lw=2)
    plt.plot(lag_time,ymod, label='wl modeled w bp')
    plt.plot(lag_time,lagmod, 'r--', label='wl modeled w bp&et')
    plt.legend(loc=4,fontsize='small')
    plt.xlim(0,lag)
    plt.ylabel('change (ft)')
    plt.xlabel('time (hrs)')
    plt.tight_layout()
    plt.savefig('l'+ os.path.splitext(impfile)[0]+'.pdf')


    plt.figure(fig_2_lab)
    plt.suptitle(fig_2_lab, x=0.2, fontsize='small')
    plt.title(os.path.splitext(impfile)[0])
    plt.subplot(4,1,1)
    plt.xcorr(yfilt_O1,zfilt_O1,maxlags=10)
    plt.ylim(-1.1,1.1)
    plt.tick_params(labelsize=8)
    plt.xlabel('lag (hrs)',fontsize='small')
    plt.ylabel('lag (hrs)',fontsize='small')
    plt.title('Cross Correl O1',fontsize='small')
    plt.subplot(4,1,2)
    plt.xcorr(yfilt_M2,zfilt_M2,maxlags=10)
    plt.ylim(-1.1,1.1)
    plt.tick_params(labelsize=8)
    plt.xlabel('lag (hrs)',fontsize='small')
    plt.ylabel('lag (hrs)',fontsize='small')
    plt.title('Cross Correl M2',fontsize='small')
    plt.subplot(4,1,3)
    plt.plot(zfftb,zffta)
    plt.tick_params(labelsize=8)
    plt.xlabel('frequency (cpd)',fontsize='small')
    plt.ylabel('amplitude')
    plt.title('WL fft',fontsize='small')
    plt.xlim(0,4)
    plt.ylim(0,30)
    plt.subplot(4,1,4)
    plt.plot(x0data,zdata, 'b')
    plt.tick_params(labelsize=8)
    plt.xlabel('julian days',fontsize='small')
    plt.ylabel('water level (ft)',fontsize='small')
    plt.twinx()
    plt.plot(x0data,f3(WLO1[2],x0data), 'r')
    plt.plot(x0data,f4(WLM2[2],x0data), 'g')
    plt.tick_params(labelsize=8)
    plt.xlim(0,10)
    plt.ylabel('tidal strain (ppb)',fontsize='small')
    plt.tick_params(labelsize=8)
    plt.tight_layout()
    plt.title('Regression Fit',fontsize='small')
    plt.savefig('f'+ os.path.splitext(impfile)[0]+'.pdf')
    plt.close()

    ###########################################################################
    #Write output to files
    ###########################################################################

    # create row of data for compiled output file info.csv
    myCSVrow = [os.path.splitext(inpfile)[0],well_name, A2_O1, A2_M2, phase_sft_O1, phase_sft_M2, delt_O1,
                delt_M2, Trans_M2, Trans_O1, Ss_O1, Ss_M2, WLO1[1], TdO1[1], WLM2[1], TdM2[1],
                WLO1[0], TdO1[0], WLM2[0], TdM2[0], WLO1[2][1], TdO1[2][1], WLM2[2][1],
                TdM2[2][1], WLO1[2][2], TdO1[2][2], WLM2[2][2], TdM2[2][2], reg_late[1], reg_early[0], aquifer_type, phsO1, phsM2]
    # add data row to compiled output file
    compfile = open('info.csv', 'a')
    writer = csv.writer(compfile)
    writer.writerow(myCSVrow)
    compfile.close()


    #export tidal data to individual (well specific) output file
    with open(outfile, "wb") as f:
        filewriter = csv.writer(f, delimiter=',')
    #write header
        header = ['xl_time','date_time','V_ugal','vert_mm','areal_mm','WDD_tam','potential','dilation_ppb','wl_ft','dbp','dwl','resid','bp','Tsoft_SG23']
        filewriter.writerow(header)
        for row in range(0,1):
            for i in range(len(d)):
            #you can add more columns here
                filewriter.writerow([xls_date[i],d[i],Grav_tide[i],vert[i],areal[i],WDD_tam[i],potential[i],
                                     dilation[i],wl[i],dbp[i],dwl[i],resid[i],bp[i],etint[i]])

    ##################    fin     #############################################

#run script on each file in processing directory
for f in os.listdir('C:\\PROJECTS\\Snake_Valley\\PYTHON\\PROCESSING'):
    if f.endswith(".csv") and f[0] != 'c' and f[0] != 'p' and f[0] != 'i' and f[0] != 'd':
        print os.path.splitext(f)[0]
        tideproc(f,"ibpdata.csv","itidaltsoft.csv")
