# -*- coding: utf-8 -*-
"""
Created on Wed Jul 26 09:07:35 2023

@author: ASOCHA

Run zonal statistics on the surface temperature rasters within the lake boundary and add stats to a table for time series analysis
"""

from rasterstats import zonal_stats

#create empty lists to store values for creating a df
date = []
meanTemp_C = []
majTemp_C = []
ninetyPercentTemp_C = []
seventyPercentTemp_C = []
maxTemp_C = []
minTemp_C = []
year = []

with rio.open(r'C:\Users\ASOCHA\OneDrive - Environmental Protection Agency (EPA)\Profile\Documents\Alpine Lakes\LandsatData\LC08_CU_003008_20210618_20210702_02_ST_B10_clip_Celcius.TIF') as src:
    array = src.read(1)
    affine = src.transform
    nodata = src.nodata

#run zonal statistics on the ST raster within the lake boundary - need to specify affine and nodata
#the output is a dict in a list so pull the dictionary out of the list
stats = zonal_stats(buff_df, array, affine = affine, nodata = nodata, stats = 'max min mean majority percentile_90 percentile_75')[0]

#get values and store them in the empty lists
file = 'LC08_CU_003008_20210618_20210702_02_ST_B10_clip_Celcius.TIF'
nameSplit = file.split('_')
fileDate = nameSplit[3]
date.append(fileDate)
fileYear = fileDate[:-4]
year.append(fileYear)

majTemp_C.append(stats['majority'])
ninetyPercentTemp_C.append(stats['percentile_90'])
seventyPercentTemp_C.append(stats['percentile_75'])
meanTemp_C.append(stats['mean'])
maxTemp_C.append(stats['max'])
minTemp_C.append(stats['min'])

#create dataframe with dates and the statistics for each date
df = pd.DataFrame(zip(date, year, minTemp_C, maxTemp_C, meanTemp_C, majTemp_C, seventyPercentTemp_C, ninetyPercentTemp_C),
                  columns = ['date', 'year', 'minTemp_C', 'maxTemp_C', 'meanTemp_C', 'majTemp_C', '75th%Temp_C', '90th%_C'])

print(df.head())