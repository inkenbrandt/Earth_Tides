# etide - Earth Tide Corrections
# use the best formulas we can, assuming no ETC from the meter!
# this turns out to be Tamura's correction scheme

import tamura
import csv
import time
import jd

filename='data.csv'
outfile='dataout4.csv'

data = csv.reader(open(filename, 'rb'), delimiter=",")
d, longit, lat, elev, gmtt= [], [], [], [], []

for row in data:
    d.append(row[0])
    longit.append(row[1])
    lat.append(row[2])
    elev.append(row[3])
    gmtt.append(row[4])

julday = []
tidal = []
#year, month, day, hours, minutes, seconds = [], [], [], [], [], []

def jul_day(d):
  # compute decimal julian day from date and time strings
  # date_str is formatted as "DD/MM/YYYY"
  # time_str is formatted as "HH:MM:SS"
  # parse the date/time string and call calc_jday() to get
  # the actual Julian Day

    yrdty = time.strptime(d,"%m/%d/%Y %H:%M")
    year = yrdty.tm_year
    month = yrdty.tm_mon
    day = yrdty.tm_mday
    hours = yrdty.tm_hour
    minutes = yrdty.tm_min
    seconds = yrdty.tm_sec
    julday = jd.calc_jday(year,month,day,hours,minutes,seconds)
    return julday
#    return year,month,day,hours,minutes,seconds

# create a list j of julian dates
for i in range(len(d)):
    julday.append(jul_day(d[i]))
#    year.append(jul_day(d[i].year))
#    month.append(jul_day(d[i]))
#    day.append(jul_day(d[i]))
#    hours.append(jul_day(d[i]))
#    minutes.append(jul_day(d[i]))
#    seconds.append(jul_day(d[i]))


def tidal_est(julday, lon, lat, elev, gmtt):
    earth_tide = tamura.tide

    for i in range(len(julday)):
    # compute Tamura ETC
        (year, month, day, hour, minute, second) = jd.un_jday(julday[i])
        C = earth_tide(year, month, day, hour, minute, second, float(lon[i]), float(lat[i]), float(elev[i]), 0.0, float(gmtt[i]))
    # Tamura's routine yields results in microgal!
        tidal.append(C/1000.0)
    return tidal

#run tidal est function
t = tidal_est(julday,longit,lat,elev,gmtt)

vert = []
for i in range(len(t)):
    #determine vertical strain from Agnew 2007
    #units are in sec squared, meaning results in mm
    vert.append(t[i] * 1.692E5 * 1E-2)

#love numbers and other constants
l = 0.0839
k = 0.2980
h = 0.6032
g = 9.821
a = 6.3707E6
det =1.692E5
delta = 1.1562
ver = (h*a)/(2*g*delta)

p = (h-3*l)/(g*a)

WDD_tam = []

for i in range(len(t)):
    WDD_tam.append(t[i]*(-9936.2956469)-7.8749754)


areal = []
for i in range(len(t)):
    #determine areal strain from Agnew 2007
    #units in mm
    areal.append(t[i]*p*1E-2)

#export to csv
with open(outfile, "wb") as f:
    filewriter = csv.writer(f, delimiter=',')
    #write header
    header = ['julday','date_time','V_mgal','vert_mm','areal_mm','WDD_tam']
    filewriter.writerow(header)
    for row in range(0,1):
        for i in range(len(d)):
            #you can add more columns here
            filewriter.writerow([julday[i],d[i],t[i],vert[i],areal[i],WDD_tam[i]])





