import geopandas
import pandas
import numpy
"""
code for calculating steepness level and the minimum qualifying sl for each link with regard to directionality 
"""

def calc_SL(length, slope):  # calculates SL for different SL aspirations (segments shorter than 50 always qualify)
    if length> 51:
        slope = abs(slope)
        sl_35, sl_5, sl_65 = 99, 99, 99
        if slope <= 0.035:
            sl_35, sl_5, sl_65 = 3.5, 5, 6.5
        elif slope <= 0.05:
            sl_5, sl_65 = 5, 6.5
            if length <= 500:
                sl_35 = 3.5
        elif slope <= 0.065:
            if length <= 150:
                sl_35, sl_5, sl_65 = 3.5, 5, 6.5
            elif length <= 500:
                sl_5, sl_65 = 5, 6.5
        elif slope <= 0.08:
            if length <= 150:
                sl_5, sl_65 = 5, 6.5
            elif length<= 500:
                sl_65 = 6.5
        elif slope <= 0.095:
            if length <= 150:
                sl_65 = 6.5
    else:
        sl_35, sl_5, sl_65 = 3.5, 5, 6.5
    return sl_35, sl_5, sl_65

def sl_signage(slope, sl):
    return sl if slope>0 else sl*(-1)
