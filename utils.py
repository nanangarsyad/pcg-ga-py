# -*- coding: utf-8 -*-
"""
Created on Sat Mar 11 11:30:35 2017

@author: NAAF
"""

from setup import ilb as _ilb
from IPython.lib.deepreload import reload as _ireload
import sys as _sys


class Utils :    
    @classmethod
    def _doLoadSubmodule(cls, module_obj:type=None) :                
        global _x
        _x = _sys.modules['helper']
        
        
        if module_obj is None:            
            _x.x_Map = _x._Map
            _x.x_Cnt = _x._Cnt
            _x.x_MtUtl = _x._MplUtils
            _x.x_CvUtl = _x._Cv2Utils
            _x.x_Utl = cls
            _x.x_Ga = _x._GA
            _x.x_ = _x 
        else :
            module_obj = getattr(_x, module_obj.__name__)              
        
        _x.__all__ = ['x_', 'x_Map', 'x_Cnt', 'x_MtUtl', 'x_CvUtl', 'x_Utl', 'x_Ga']
            
    
    @staticmethod 
    def reloadAllSubmodule():       
        _ireload(_x)
        Utils._doLoadSubmodule() # load all submodule
        
    @staticmethod        
    def reloadSubModule(sub_module:type):
        _ireload(sub_module)        
        Utils._doLoadSubmodule(sub_module)