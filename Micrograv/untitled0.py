# -*- coding: utf-8 -*-
"""
Created on Thu Aug 08 13:22:05 2013

@author: paulinkenbrandt
"""

import numpy
import numpy.f2py as f2py


#f2py.info.__package__('Etidefunc.f')

#f2pywrapFirstHorzTideStrain3
#print Etidefunc_module.DryTide8(100,41.12,234,1700)


p = f2py.f2py2e.run_main(['-m','Etidefunc','Etidefunc.f'])

import Etidefunc