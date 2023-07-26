# -*- coding: utf-8 -*-
"""
Created on Thu Jun 29 14:10:46 2023

@author: ASOCHA

Reclassify the surfact temperature raster by applying the scale factor from USGS and converting from kelvin to celcius
"""

#create function to apply scale factor and convert to degrees celcius
def tempToCelcius(val):
    return (val) * 0.00341802 + 149 - 273.15

#get ST raster that's been clipped
with rio.open(out_tif) as src:
    temp = src.read(masked=True)
    profile = src.profile

#apply conversion function
tempCel = tempToCelcius(temp)

#change the raster dytpe to float to conserve decimals
profile.update(dtype=rio.float32)

with rio.open(r'C:\Users\ASOCHA\OneDrive - Environmental Protection Agency (EPA)\Profile\Documents\Alpine Lakes\LandsatData\LC08_CU_003008_20210618_20210702_02_ST_B10_clip_Celcius.TIF', 'w', decimal_precision=3,  **profile) as dst:
    dst.write(tempCel)