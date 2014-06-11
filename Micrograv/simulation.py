#this file takes data from a csv named data and outputs a csv named dataout
#the dataout file contains tida signal

import tamura
import csv
import time
import math

filename='PW20.csv'
outfile='dataout.csv'

#open data file and read in data
data = csv.reader(open(filename, 'rb'), delimiter=",")
d, longit, lat, elev, gmtt, wl= [], [], [], [], [], []

# d is the date M/D/YYYY H:MM
#longit is the longitude
#lat is the latitude
#elev is the elevation
#gmtt is the offset from utc; utah is -7; utc is 0
for row in data:
    d.append(row[0])
    longit.append(row[1])
    lat.append(row[2])
    elev.append(row[3])
    gmtt.append(row[4])
    wl.append(row[5])

#create spaces for output of julian day and tidal functions
julday = []
tidal = []


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


# create a list of julian dates
for i in range(len(d)):
    julday.append(jul_day(d[i]))


#define the various components of the date, represented by d
yrdty = []
year = []
month = []
day = []
hours =[]
minutes = []
seconds = []

for i in range(len(d)):
    yrdty.append(time.strptime(d[i],"%m/%d/%Y %H:%M"))
    year.append(yrdty[i].tm_year)
    month.append(yrdty[i].tm_mon)
    day.append(yrdty[i].tm_mday)
    hours.append(yrdty[i].tm_hour)
    minutes.append(yrdty[i].tm_min)
    seconds.append(yrdty[i].tm_sec)

#tidal estimation function calling from tamura.py script
def tidal_est(year,month,day,hours,minutes,seconds, lon, lat, elev, gmtt):
    earth_tide = tamura.tide

    for i in range(len(julday)):
    # compute Tamura ETC
        #(year, month, day, hour, minute, second) = jd.un_jday(julday[i])
        C = earth_tide(year[i], month[i], day[i], hours[i], minutes[i], seconds[i], float(lon[i]), float(lat[i]), float(elev[i]), 0.0, float(gmtt[i]))
    # Tamura's routine yields results in microgal!
        tidal.append(C/1000.0)
    return tidal

#run tidal est function
t = tidal_est(year,month,day,hours,minutes,seconds,longit,lat,elev,gmtt)
print t
#define variabel for vertical strain
vert = []
for i in range(len(t)):
    #determine vertical strain from Agnew 2007
    #units are in sec squared, meaning results in mm
    vert.append((t[i]) * 1.692 * 1E3)

#love numbers and other constants
#from Agnew 2007
l = 0.0839
k = 0.2980
h = 0.6032
#gravity m/s**2
g = 9.821
a = 6.3707E6
det =1.692E5
delta = 1.1562
gamma = 0.6948
ver = (h*a)/(2*g*delta)
p = 7.692E5


#lamb_N = []
#for i in range(len(t)):
#    lamb_N.append(-0.6948/(g*a)*t[i])
#
#lamb_E = []
#for i in range(len(t)):
#    lamb_E.append(0.6948/(g*a*math.sin(float(lat[i]))*t[i]))

#WDD is used to recreate output from TSoft
Grav_tide =[]
for i in range(len(t)):
    Grav_tide.append(t[i]*-1000)


WDD_tam = []
for i in range(len(t)):
    WDD_tam.append(t[i]*(-9936.2956469)-7.8749754)


areal = []
for i in range(len(t)):
    #determine areal strain from Agnew 2007
    #units in mm
    areal.append(t[i]*p*1E-2)

potential = []
for i in range(len(t)):
    potential.append(-318.49681664*(t[i]*1000) - 0.50889238)

#dilation from relationship defined using Harrison's code
dilation = []
for i in range(len(t)):
    dilation.append(-0.381611837*1000*t[i] - 0.000609517)

#export to csv
with open(outfile, "wb") as f:
    filewriter = csv.writer(f, delimiter=',')
    #write header
    header = ['julday','date_time','V_ugal','vert_mm','areal_mm','WDD_tam','potential','dilation_ppb','wl_ft']
    filewriter.writerow(header)
    for row in range(0,1):
        for i in range(len(d)):
            #you can add more columns here
            filewriter.writerow([julday[i],d[i],Grav_tide[i],vert[i],areal[i],WDD_tam[i],potential[i],dilation[i],wl[i]])





