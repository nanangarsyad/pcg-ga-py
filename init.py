# -*- coding: utf-8 -*-
"""
Created on Mon Mar  6 09:34:09 2017

@author: NAAF
"""
from setup import cv2, mpl, plt, np

MAP_WIDTH = 5000
MAP_HEIGHT= 5000


# Init the module
try             : raw     
except NameError: raw = None    
else            : pass

try             : hmap     
except NameError: hmap = None
else            : pass

if raw is None  :     
    raw = open('y_map.dat', 'rb')
if hmap is None :    
    hmap = np.fromfile(raw, np.float32)    
    hmap = np.reshape(hmap, (MAP_WIDTH, MAP_HEIGHT))
    raw.close()

mpl.style.use('dark_background')
