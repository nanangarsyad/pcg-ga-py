# -*- coding: utf-8 -*-
"""
Created on Wed Mar  1 09:51:25 2017

@author: NAAF
"""
#Init import
from setup import cv2 as _cv2, \
                  mpl as _mpl, \
                  plt as _plt, \
                  np as _np
from typing import Tuple as _Tuple
import sys as _sys
import inspect as _inspect
from utils import Utils as _Utils


class _Map:

    @staticmethod
    def convTo32fc1Norm(hmap: _np.ndarray) -> _Tuple[_np.ndarray, float, float]:
        """
        convert actual hmap to 0-1 (normalize) 32fc1, 
        with value less than low_limt clamped to low_limit
        """
        try             : del hmap_32fc1_norm   # clear the memory if already exist
        except NameError: pass                  # do nothing    
          
        low_limit = _np.partition(hmap[hmap > 0], 0)[0]  # Get the lower limit
        high_limit = hmap.max()
        hmap_32fc1_norm = _np.where(hmap > low_limit, hmap, low_limit)
        #hmap_32fc1_norm -= low_limit    # Make sure the hmap started from 0                
        N = 1.0/hmap_32fc1_norm.max()   # The normalizer
        hmap_32fc1_norm *= N
        return hmap_32fc1_norm, low_limit, high_limit, N
    
    @staticmethod
    def getAreaForH(hmap_32fc1_norm:_np.ndarray, normalizer:float, 
                    h_min:float, h_max:float)\
        -> _Tuple[_np.ndarray, list, list] :
        """
        Get area of coverage between the specified h_min and h_max (inclusive,     \
        lower and upper bound), if the n_max = None, won't use upper bound, also   \
        applied for the h_min                                                                
        @ret contours 
        @ret hierarchy
        """   
        hmap = hmap_32fc1_norm
        try     : h_min *= normalizer
        except  : pass #the_type, the_value, the_traceback = sys.exc_info()
        
        try     : h_max *= normalizer        
        except  : pass #the_type, the_value, the_traceback = sys.exc_info()
        
        if h_max is None :
            sel_map = _np.where(hmap >= h_min, 255, 0)  #Binary threshold  
        elif h_min is None :
            sel_map = _np.where(hmap <= h_max, 255, 0)  #Binary threshold  
        else :
            sel_map = _np.where((hmap >= h_min) & (hmap <= h_max), 255, 0)  #Binary threshold
        sel_map = sel_map.astype(_np.uint8)
        sel_image, countours, hierarchy = \
            _cv2.findContours(sel_map, _cv2.RETR_TREE, _cv2.CHAIN_APPROX_SIMPLE)
        
        #return sel_map, \
        del sel_map
        return {'cntr':countours, 
                'hrar':hierarchy}
    
    @staticmethod
    def splitMap(hmap:_np.ndarray, split:list) -> _Tuple[_np.ndarray, float, list]:        
        """
        split the map.
        in  : 
            hmap (ori),
            split (the splitter)
        out : 
            hmap_normalized, 
            normalizer,
            splitted_map (masked-map, contours, hierarchy) list
        """
        hmap_normz, lowlim, hilim, normz = _Map.convTo32fc1Norm(hmap)        
        return hmap_normz, lowlim, hilim, normz, \
               [_Map.getAreaForH(hmap_normz, normz, x[0], x[1]) for x in split]
    
class _Cnt :
    
    @staticmethod
    def getCentroid(cntr:_np.ndarray) :
        moments = _cv2.moments(cntr)
        if moments['m00'] != 0.0:
            cx = moments['m10']/moments['m00']
            cy = moments['m01']/moments['m00']
            centroid = (cx,cy)
            return centroid
        else:
            return None
        
class _MplUtils:
    @staticmethod
    def plot3d(hmap:_np.ndarray, normalized:bool) :
        from mpl_toolkits.mplot3d import Axes3D
        
        fig = _plt.figure()
        ax = fig.gca(projection='3d')        
        if normalized :
            X, Y = _np.meshgrid(
                    _np.linspace(0, 1, 5000),   # X axis range
                    _np.linspace(0, 1, 5000))   # Y axis range
        else :                
            X, Y = _np.meshgrid(
                    _np.arange(0, 5000, 1),   # X axis range
                    _np.arange(0, 5000, 1))   # Y axis range                    
        surf = ax.plot_surface(
                X, Y , hmap,
                cmap=_mpl.cm.coolwarm,
                antialiased=False)
        fig.colorbar(surf, shrink=0.5, aspect=5)
        _plt.show()     
    
    @staticmethod
    def draw2dContour(cntrs:list, shape:tuple):
        img = _np.zeros(shape, dtype=_np.uint8)
        _cv2.drawContours(img, cntrs, 0, 255, -1)
        _plt.imshow(img, cmap='gray')  
        del img
        

class _Cv2Utils:
    @staticmethod
    def plot2d(hmap:_np.ndarray) :
        if _cv2.getWindowProperty('img', 0 ) == -1 :
            _cv2.namedWindow('img', _cv2.WINDOW_NORMAL)
            
        _cv2.imshow('img', hmap)

class MapManager:    
    
    def __init__(self, hmap:_np.ndarray, split_naming:dict):                
        self.m_mapData,  \
        self.m_lowLimit, self.m_hiLimit, \
        self.m_normz, splitted = _Map.splitMap(hmap, list(split_naming.values()))    
        
        self.m_mapSplit = dict(zip(list(split_naming.keys()), splitted))        
        
        for b in list(split_naming.values()):
            if b[0] == None :  # lower limit (b[0]) with value of None, without                             
                b[0] = 0       # doubt would be the lowest limit
            elif b[1] == None :   # upper limit(b[1]) exactly the 
                b[1] = hmap.max() # oposite of lowe limit
            
        self.m_mapBorder = split_naming                
        self.m_mapAttrs = {}    
        
    def _do_terrain_name_splitting(self):
        self.m_mapAttrs['']
        pass
        
    
    def _get_includes (self):
        return {**self.__dict__, \
                **dict(_inspect.getmembers(self, predicate=_inspect.ismethod))}
    
    def add_attr(self, attr_name:str, attr_init:str, attr_logic:str):   
        """
        Add attribute to the map
        In:
            attr_name (str): The attribute name will be added.
            attr_init (str):  The command being used to initialize the attribute.
                The strin shouldn't be a statement as the string will be 
                evaluated with `eval()`. Note, this (self) class member will be
                accessed likes a globals() variable should be.
            attr_logic (str): The command being used for applying the rule for 
                the attribute.No strict restriction being imposed, so think about 
                this command like an external python script :-). Note, this (self) 
                class member shall be accessed likes a globals() variable should be.
        Out:
            None            
        """                
        self.m_mapAttrs[attr_name] = eval(attr_init, globals(), self._get_includes())        
        exec(attr_logic, globals(), self._get_includes())
        pass
    
    def normalize(self, val):
        return val*self.m_normz
    
    def denormalize(self, val):
        return val/self.m_normz

class GaManager:
    def __init__(self, mapManager:MapManager):         
        self.m_mapManager = mapManager
        self.m_landmark_types = {}        
        self.m_fit_rules_p1 = {}    
        self.m_fit_rules_p2 = {}    
    def add_landmark_desc(self, lmark_name:str, lmark_rule:str):        
        pass
    
    def add_landmark_village(self) :
        #desc: village should be placed between 725-730 H        
        size = (50, 50) # landmark size
        hmin = self.m_mapManager.normalize(725)
        hmax = self.m_mapManager.normalize(730)
        stride = size[0] # first jump size, will change by evolution

        npop = 25 # number of population
        
        #random                      
        sel = _np.arange(0, 5000, 1)
        ysel = _np.ones(5000, dtype=_np.bool)     
        ysel[-stride:] = False # remove the last {size} data, prevent OutOfBound 
        xsel = _np.ones(5000, dtype=_np.bool)     
        xsel[-stride:] = False
        solution =[]

        for n in range(npop):
            xs = _np.random.choice(sel[xsel], 1)
            xsel[xs[0]:xs[0]+stride] = False # Remove the one got used 
            ys = _np.random.choice(sel[ysel], 1)
            ysel[ys[0]:ys[0]+stride] = False # Remove the one got used 
            solution.append((xs, ys, size[0], size[1]))
            
        #fitness        
        mapData = self.m_mapManager.m_mapData  
        coor = []
        fitness = []
        [
            (
                coor.append((j,j)), fitness.append(_np.count_nonzero(
                (mapData[j:j+stride,j:j+stride] >= hmin) &
                (mapData[j:j+stride,j:j+stride] <= hmax)))
            )
            for j in _np.arange(0, 5000, stride)
        ]        
        fitness = _np.array(fitness)
        vi = _np.argwhere(fitness >= fitness.max())
        good = _np.random.choice(vi.ravel(), 1)         
        #print (good)
        return good, coor[good[0]], size
        
    def add_fitness_rule_p1(self):
        pass
    
    def add_fitness_rule_p2(self, rule_name:str, rule_logic:str):
        self.m_fit_rules_p1['rule_name'] = rule_logic
    
    
    def start_simulation(self):
        #phase 1, distribute landmark
        
        
        #Initial random seed 
        
        for rule_name, rule_logic in self.m_fit_rules_p2.items() :
            print ('#applying rule : ' + rule_name)
        
#    add_landmark_desc('village', 
#                      #desc: village should be placed between 725-730 H
#                      """                      
#                      size = (50, 50) # landmark size
#                      h_min = normalize(725)
#                      h_max = normalize(730)
#                      jump = size[0] # first jump size, will change by evolution
#                      
#                      npop = 25 # number of population
#                      
#                      #random                      
#                      sel = _np.arange(0, 5000, 1)
#                      ysel = _np.ones(5000, dtype=np.bool)     
#                      ysel[-size:] = False # remove the last {size} data, prevent OutOfBound 
#                      xsel = _np.ones(5000, dtype=np.bool)     
#                      xsel[-size:] = False
#                      solution =[]
#                      
#                      for n in range(npop):
#                          xs = _np.random.choice(sel[xsel], 1)
#                          xsel[xs[0]:xs[0]+size] = False # Remove the one got used 
#                          ys = _np.random.choice(sel[ysel], 1)
#                          ysel[ys[0]:ys[0]+size] = False # Remove the one got used 
#                          solution.append((xs, ys, size, size))
#                          
#                      #fitness                       
#                      solution_fit = [
#                         np.count_nonzero(
#                                 (m_mapData[j:j+jump,j:j+jump] >= hmin) &
#                                 (m_mapData[j:j+jump,j:j+jump] <= hmax))  
#                         for j in np.arange(0, 5000, jump) 
#                      ]
#                      good = np.random.choice(xmap[xmap == 2], 1)
#                      
#                      """)
    
            
        
        
class _GA :
    @staticmethod
    def attributingTerrain1(
            hmap_normalized:_np.ndarray, 
            splitted_terrain:list,
            naming:list):
        """
        Do naming the splitted terrain by H, base DNA, which is made availble 
        by countour_feature.py
        """
        mat_atr = _np.zeros(hmap_normalized.shape)

        ret = {'map_ori': hmap_normalized,
               'map_attr':hmap_normalized
               }        
        return dict(ret, **zip(naming, splitted_terrain))
        
    
    @staticmethod
    def attributingTerrain2(
            hmap_normalized:_np.ndarray, 
            splited_terrain:list,
            behav):
        """
        do custom attributing based on user preference, in regard with user 
        imagination. e.g 
        """
        
        pass
    
    
    @staticmethod
    def attributingGameObject(
            # the param

            ) :
        pass
    
    @staticmethod
    def newmethod() :
        pass
    
    @staticmethod
    def startSimulation(
            hmap_normalized:_np.ndarray):        
        # Randomizing landmark position (seed)        
        # Find fitness value 
        # Selection #1, cross breed, the selected individu
        # Find Fitness again
        # Selection #2, Mutate, 
        pass
    
_x = _sys.modules[__name__]
_Utils._doLoadSubmodule()    
print ('loaded')