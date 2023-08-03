# -*- coding: utf-8 -*-
"""
Created on Wed Aug  2 14:37:38 2023

Rewriting Amalia Handler's mountain idenfication in python based on the USGS landforms categories

@author: ASOCHA
"""
import tkinter as tk
from tkinter.filedialog import askdirectory, askopenfilename
import geopandas as gpd
import rasterio as rio
from rasterstats import zonal_stats
import pandas as pd
import os

#get rid of root window
root = tk.Tk()
root.withdraw()

#make sure window comes to front
root.attributes('-topmost', 1)

#ask user to select folder for directory
wd = askdirectory(title = 'Select Directory Folder')
print('Setting working directory:\n', wd, '\n')
os.chdir(wd)

#get lake boundary file
lakes = askopenfilename(title = 'Select Lake Boundary File')
print('Lake boundary file:\n', lakes, '\n')

# Reading in the input file
input_df = gpd.read_file(lakes)

#get landforms file
landforms_file = askopenfilename(title = 'Select Landforms File')

#read raster, save attributes for zonal stats
landforms_src = rio.open(landforms_file)
landforms_arr = landforms_src.read(1)
affine = landforms_src.transform
nodata = landforms_src.nodata

#set buffer **make sure to check crs, for both these files, NAD83 AEA is used and its units are meters which is what we want
buffer = 1000

#copy df and buffer all geometries out to specified distance
buff_df = input_df
buff_df.geometry = buff_df.geometry.buffer(buffer)

#%%
UNIQUE_ID =[]
low_mtn = []
high_mtn = []
#iterate through buffered dataframe to get each lake and its boundary
for i in range(len(buff_df)):
    ID = buff_df.loc[i, 'UNIQUE_ID']
    UNIQUE_ID.append(ID)
    geom = buff_df.loc[i, 'geometry']
    
    #get total pixel count, need to specify affine and nodata to prevent errors and warnings
    print(f'Getting pixel count for {ID}\n')
    tot_pix = zonal_stats(geom, landforms_arr, affine = affine, nodata = nodata)[0]['count']
    
    #get counts for each pixel value within the polygon
    unique_counts = zonal_stats(geom, landforms_arr, affine = affine, nodata = nodata, categorical = True)[0]
    
    if 8 in unique_counts:
        low_mtn_pix = unique_counts[8]
    else:
        low_mtn_pix = 0
    
    if 9 in unique_counts:
        high_mtn_pix = unique_counts[9]
    else:
        high_mtn_pix = 0

    low_mtn.append(low_mtn_pix)
    high_mtn.append(high_mtn_pix)
    
out_df = pd.DataFrame(zip(UNIQUE_ID, low_mtn, high_mtn), columns = ['UNIQUE_ID', 'Low_Mtn_count', 'High_Mtn_count'])
out_df.to_csv(f'NLA_integrated_sample_mtnlakes_{buffer}m.csv')
    
    
    
    