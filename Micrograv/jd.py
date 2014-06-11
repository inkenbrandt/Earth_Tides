# jd.py - Julian Day calculations; convert from calendar to JD and back
# includes handling for fractional days.

import sys
import string
import math

def jul_day(date_str, time_str):
  # compute decimal julian day from date and time strings
  # date_str is formatted as "YY/MM/DD"
  # time_str is formatted as "HH:MM:SS"
  # parse the date/time string and call calc_jday() to get
  # the actual Julian Day
  fields = string.split(date_str,"/")
  year = int(fields[0])
  month = int(fields[1])
  day = int(fields[2])
  if year < 90:
    year = year + 100
  year = year + 1900
  fields = string.split(time_str, ":")
  hours = int(fields[0])
  minutes = int(fields[1])
  seconds = int(fields[2])
  return calc_jday(year, month, day, hours, minutes, seconds)

def str2jd(date_str, time_str):
  # compute decimal julian day from date and time strings
  # date_str is formatted as "YYYY/MM/DD"
  # time_str is formatted as "HH:MM:SS"
  # parse the date/time string and call calc_jday() to get
  # the actual Julian Day
  fields = string.split(date_str,"/")
  year = int(fields[0])
  month = int(fields[1])
  day = int(fields[2])
  fields = string.split(time_str, ":")
  hours = int(fields[0])
  minutes = int(fields[1])
  seconds = int(round(float(fields[2])))
  return calc_jday(year, month, day, hours, minutes, seconds)

def str2jd2(date_str, time_str):
  # compute decimal julian day from date and time strings
  # date_str is formatted as "MM/DD/YYYY"
  # time_str is formatted as "HH:MM:SS"
  # parse the date/time string and call calc_jday() to get
  # the actual Julian Day
  fields = string.split(date_str,"/")
  month = int(fields[0])
  day = int(fields[1])
  year = int(fields[2])
  fields = string.split(time_str, ":")
  hours = int(fields[0])
  minutes = int(fields[1])
  seconds = int(fields[2])
  return calc_jday(year, month, day, hours, minutes, seconds)

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

def un_jday(jul_day):
  Months = [0, 31, 61, 92, 122, 153, 184, 214, 245, 275, 306, 337]
  M_len = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
  jul_day = jul_day + 0.5 # shift to noon
  fract_day = jul_day % 1 
  fract_day = round(fract_day, 5)
  JD = math.floor(jul_day)
  if fract_day < 0.0:
    fract_day = fract_day + 1
    JD = JD-1
  # undo JD calc
  Q1 = math.floor((JD-59)/1461.0)
  R1 = (JD-59)%1461.0
  Q2 = math.floor(R1/365.0)
  R2 = R1%365.0
  Year = 4*Q1 + Q2 - 4712
  D = R2+13
  if R1 == 1460 and Q2 == 4 and R2 == 0:
    # date is 12 March of a leap year, and need to reduce offset by 1
    # between Julian and Greg. calendars
    D = D-1 
  # find month of year
  index = -1
  for i in range(len(Months)):
    if Months[i] < D:
      if i > index:
	index = i
  # find day of month
  Day = D - Months[index]
  Month = index + 3
  if Month > 12:
    Year = Year + 1
    Month = Month - 12
  # handle leap years
  if (Year%4) == 0:
    M_len[1] = 29 # keeps trap below from tripping
  hour = fract_day * 24.0
  minute = (hour%1.0)*60.0
  second = round((minute%1.0)*60.0)
  hour = math.floor(hour)
  minute = math.floor(minute)
  # trap for unreasonable times (e.g. hour 25, minute 61)
  if second >= 60:
    minute = minute+1;
    second = second-60;
  if minute >= 60:
    minute = minute-60;
    hour = hour+1;
  if hour >= 24:
    hour = hour - 24;
    Day = Day + 1;
  # trap for unreasonable dates; i.e. Feb 30 = Mar 2
  if Day > M_len[Month-1]:
    Day = Day - M_len[Month-1]
    Month = Month+1
  # return 
  return(int(Year), int(Month), int(Day), int(hour), int(minute), int(second))

def datestr(jday):
  (year, month, day, hour, minute, second) = un_jday(jday)
  return "%04d/%02d/%02d %02d:%02d:%02d" % (year, month, day, hour, minute, second) 

def datestr2(jday):
  (year, month, day, hour, minute, second) = un_jday(jday)
  return "%02d/%02d/%04d %02d:%02d:%02d" % (month, day, year, hour, minute, second) 

def fract_day(time_str):
  # compute fraction of a day given a HH:MM:SS string
  fields = string.split(time_str, ":")
  hours = float(fields[0])
  minutes = float(fields[1])
  seconds = float(fields[2])
  return (hours + (minutes/60.0) + (seconds/3600.0)) / 24.0

