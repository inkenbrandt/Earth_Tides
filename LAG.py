# -*- coding: utf-8 -*-
"""
Created on Thu Dec 19 06:32:15 2013

@author: paulinkenbrandt
"""

import numpy, scipy
import csv
from scipy.signal import correlate

impfile=
data = csv.reader(open(impfile, 'rb'), delimiter=",")
dy, u, l, nm, d, wl, t, vert =[], [], [], [], [], [], [], []


# Load datasets, taking mean of 100 values in each table row
A = numpy.loadtxt("vb-sync-XReport.txt")[:,1:].mean(axis=1)
B = numpy.loadtxt("vb-sync-YReport.txt")[:,1:].mean(axis=1)

nsamples = A.size

# regularize datasets by subtracting mean and dividing by s.d.
A -= A.mean(); A /= A.std()
B -= B.mean(); B /= B.std()

# Put in an artificial time shift between the two datasets
time_shift = 20
A = numpy.roll(A, time_shift)

# Find cross-correlation
xcorr = correlate(A, B)

# delta time array to match xcorr
dt = numpy.arange(1-nsamples, nsamples)

recovered_time_shift = dt[xcorr.argmax()]

print "Added time shift: %d" % (time_shift)
print "Recovered time shift: %d" % (recovered_time_shift)

# SAMPLE OUTPUT:
# Added time shift: 20
# Recovered time shift: 20