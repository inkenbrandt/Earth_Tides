# -*- coding: utf-8 -*-
"""
Created on Wed Aug 07 07:42:40 2013

@author: paulinkenbrandt
"""
import csv
import numpy
import scipy.optimize as optimization

impfile = 'dataout.csv'



# Generate artificial data = straight line with a=0 and b=1
# plus some noise.
#xdata = numpy.array([0.0,1.0,2.0,3.0,4.0,5.0])
#ydata = numpy.array([0.1,0.9,2.2,2.8,3.9,5.1])
# Initial guess.
#x0    = numpy.array([0.0, 0.0, 0.0])
#
#sigma = numpy.array([1.0,1.0,1.0,1.0,1.0,1.0])
#
#def func(x, a, b, c):
#    return a + b*x + c*x*x
#
#print optimization.curve_fit(func, xdata, ydata, x0, sigma)



data = csv.reader(open(impfile, 'rb'), delimiter=",")
julday, t, vert, areal, WDD_tam= [], [], [], [], []

for row in data:
    julday.append(row[0])
    t.append(row[1])
    vert.append(row[2])
    areal.append(row[3])
    WDD_tam.append(row[4])

xdata = numpy.array(julday)
ydata = numpy.array(t)

print xdata