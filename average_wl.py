# -*- coding: utf-8 -*-
"""
Created on Wed Jun 25 16:14:51 2014

@author: paulinkenbrandt
"""

import pandas as pd
import numpy as np
import math
import tamura
import matplotlib.pyplot as plt
import statsmodels.tsa.tsatools as tools
from pandas import ExcelWriter

lag = 200

df = pd.io.excel.read_excel("C:\Users\PAULINKENBRANDT\Downloads\E5382-MonitoringData (1)\North_Side_Weirs.xlsx","Main", index_col=0)
wld = df.resample('60Min')

wld['NB_wl_std']=pd.stats.moments.rolling_std('NB_ft_water',24)
wld['NB_wl_avg']=pd.stats.moments.rolling_mean('NB_ft_water',24)


wld['NB_ft_water'].plot(style='k--')
wld['NB_wl_avg'].plot(style='k')

wldata = wld.ix[1050:]

wldata['rollmean'] = pd.rolling_mean(wldata['wlelev_m'],30)
wldata['wlnorm'] = (wldata['wlelev_m']- wldata['wlelev_m'].mean())/(wldata['wlelev_m'].max() - wldata['wlelev_m'].min())
wldata['bpnorm'] = (wldata['bp_mH2O']- wldata['bp_mH2O'].mean())/(wldata['bp_mH2O'].max() - wldata['bp_mH2O'].min())
wldata['tempnorm'] = (wldata['temp']- wldata['temp'].mean())/(wldata['temp'].max() - wldata['temp'].min())
wldata['condnorm'] = (wldata['cond']- wldata['cond'].mean())/(wldata['cond'].max() - wldata['cond'].min())
wldata['dwl'] = wldata['wlelev_m'].diff()
wldata['dbp'] = wldata['bp_mH2O'].diff()


########################################################   date conversion
#function to convert date into julian date
def jday(Y, M, D, h, m, s):
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


wldata['year'] = wldata.index.year
wldata['month'] = wldata.index.month    
wldata['day'] = wldata.index.day
wldata['hour'] = wldata.index.hour
wldata['minute'] = wldata.index.minute
wldata['second'] = wldata.index.second

year = wldata['year'].values
month = wldata['month'].values
day = wldata['day'].values
hour = wldata['hour'].values
minute = wldata['minute'].values
second = wldata['second'].values

d = [jday(year[i],month[i],day[i],hour[i],minute[i],second[i]) for i in range(len(year))]

wldata['d']=d

#converting the julian dates to excel dates
xls_date = np.array([(float(d[i])-2415018.5) for i in range(len(d))])

wldata['xlsdate'] = xls_date
wldata.to_clipboard()

########################################################## Calculate Earth Tide

 #run tidal function
t = [(tamura.tide(year[i], month[i], day[i], hour[i], minute[i], second[i], -113.97, 39.28, 1500.0, 0.0, -7.0)) for i in range(len(d))]

####################################################

wldata['tides'] = t

wl = wldata['wlnorm'].values
bp = wldata['bpnorm'].values

x = np.array(bp)
y = np.array(wl)

dt = []
mn = np.mean(t)
std = np.std(t)
for i in range(len(t)):
    dt.append((t[i]-mn)/std)


z = np.array(dt)


# create lag matrix for regression
bpmat = tools.lagmat(x,lag, original='in')
etmat = tools.lagmat(z,lag, original='in')
lamat = np.column_stack([bpmat,etmat])

#transpose matrix to determine required length
#run least squared regression
sqrd = np.linalg.lstsq(bpmat,y)
sqrdlag = np.linalg.lstsq(lamat,y)

wlls = sqrd[0]
lagls = sqrdlag[0]

cumls = np.cumsum(wlls)
lagcumls =np.cumsum(lagls)

ymod = np.dot(bpmat,wlls)
lagmod = np.dot(lamat,lagls)

alpha = lagls[0:len(lagls)/2]
alpha_cum = np.cumsum(alpha)
gamma = lagls[len(lagls)/2:len(lagls)]
gamma_cum = np.cumsum(gamma)

lag_time = (xls_date - xls_date[0])*24


plt.figure()
plt.subplot(2,1,1)
plt.plot(lag_time[0:len(cumls)],cumls, label='b.p. response')

plt.xlabel('lag (hr)')
plt.ylabel('cumulative response function')
plt.legend(loc=4,fontsize='small')
plt.subplot(2,1,2)
plt.plot(lag_time,wl, label='wl', lw=2)
plt.plot(lag_time,ymod, label='wl modeled w bp')
plt.plot(lag_time,lagmod, 'r--', label='wl modeled w bp&et')
plt.legend(loc=4,fontsize='small')
plt.xlim(0,lag)
plt.ylabel('change (ft)')
plt.xlabel('time (hrs)')
plt.tight_layout()
plt.show()

writer = ExcelWriter("C:\\Users\\PAULINKENBRANDT\\Documents\\GitHub\\Earth_Tides\\Millville_WLBP.xlsx")
wldata.to_excel(writer,'sheet2')