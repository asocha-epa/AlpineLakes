# -*- coding: utf-8 -*-
"""
Created on Wed Jul 12 09:09:47 2023

Check if there are actual values withing lake area for ST rasters downloaded since bounding boxes are still large
and intersect the lake area even with no data actually in those areas

@author: ASOCHA
"""

import geopandas as gpd
import rasterio as rio
import os
from rasterstats import zonal_stats

# lakes = r'C:\Users\ASOCHA\OneDrive - Environmental Protection Agency (EPA)\Profile\Documents\Alpine Lakes\NLA_Integrated_Lakes.gpkg'
# data = gpd.read_file(lakes)

wd = r'D:\AlpineLakes\LandsatARD'
#wd= r'C:\Users\asocha\OneDrive - Environmental Protection Agency (EPA)\Profile\Documents\Alpine Lakes\LandsatData' #this one is for laptop
os.chdir(wd)

#read in lake shapefile, convert to wgs84, and get bounding box values for running search
shp = gpd.read_file(r'C:\Users\asocha\OneDrive - Environmental Protection Agency (EPA)\Profile\Documents\Alpine Lakes\Tahoe_Soils_and_Hydro_Data\Tahoe_Soils_and_Hydro_Data.shp')

#read in surface temperature raster and get the transform and nodata for running zonal stats
with rio.open(r'.\1985\LT05_CU_003008_19850701_20210422_02_ST\LT05_CU_003008_19850701_20210422_02_ST_B6.TIF') as src:
    array = src.read(1)
    affine = src.transform
    nodata = src.nodata

#run zonal stats to get the sum. the output is a dictionary in a list, so get that part by itself
#if sum is none, the areas don't intersect and the raster can be ignored
stats = zonal_stats(shp, array, affine = affine, nodata = nodata, stats = 'sum')[0]

print(stats['sum'])