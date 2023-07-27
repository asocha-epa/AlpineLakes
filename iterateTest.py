# -*- coding: utf-8 -*-
"""
Created on Wed Jul 26 13:27:16 2023

@author: ASOCHA

Initial testing for combining lake temperature data processing in one script and iterating the process for all files downloaded
Working to make additional scripts into functions and modules that can be imported for a cleaner script
"""
import os
import tkinter as tk
from tkinter.filedialog import askdirectory
import rasterio as rio
import geopandas as gpd
import ClipToLake2

#get rid of root window
root = tk.Tk()
root.withdraw()


# Reading in the input shapefile.
input_df = gpd.read_file(r'C:\Users\asocha\OneDrive - Environmental Protection Agency (EPA)\Profile\Documents\Alpine Lakes\Tahoe_Soils_and_Hydro_Data\Tahoe_Soils_and_Hydro_Data.shp')

# Reading the input CRS. 
input_crs = input_df.crs

# Reprojecting the data. If needed, substitute "WXYZ" with relevant EPSG code
#input_df = input_df.to_crs('epsg:WXYZ')

# Creating the variable-sized buffer
input_df['buffer'] = input_df.buffer(-100)

# Dropping the original geometry and setting the new geometry
buff_df = input_df.drop(columns=['geometry']).set_geometry('buffer')

# Reprojecting the buffered data back to the CRS used in the original input shapefile
buff_df = buff_df.to_crs(input_crs)

#%%
#ask user to select folder for directory
print('select folder', "\n")
wd = askdirectory(title = 'Select Directory Folder')

#go through each folder and subfolder in the root folder to get raster files, skipping the tar zip files              
for folder in os.listdir(wd):
    rootDir = os.path.join(wd, folder)
    for root, subDirs, files in os.walk(rootDir):
        for subDir in subDirs:
            newDir = os.path.join(rootDir, subDir)
            os.chdir(newDir)
            if subDir.endswith('.tar'):
                continue
            else:
                #get the QA and the surface temperature bands, save name for exporting files
                for file in os.listdir('.'):
                    if file.endswith('QA_PIXEL.TIF'):
                        QA_band = file
                        QA_name = file[:-4]
                    if file.endswith('ST_B10.TIF') or file.endswith('ST_B6.TIF'):
                        ST_band = file
                        ST_name = file[:-4]
                        
                        #read in raster bands
                        surfTemp = rio.open(ST_band)
                        ST_array = surfTemp.read()
                        profile = surfTemp.profile
                        
                        QA = rio.open(QA_band)
                        QA_array = QA.read()
                        
                        #project lake df to the same crs
                        buff_df = buff_df.to_crs(surfTemp.crs)
                        
                        #run functions from ClipToLake2 script, **clipRaster output is a tuple with the array and the meta
                        coords = ClipToLake2.getFeatures(buff_df)
                       
                        QA_clip = ClipToLake2.clipRaster(QA, coords)
                        QA_clip_array = QA_clip[0]
                        QA_clip_meta = QA_clip[1]
                        
                        ST_clip = ClipToLake2.clipRaster(surfTemp, coords)
                        ST_clip_array = QA_clip[0]
                        ST_clip_meta = QA_clip[1]
                        
                        
                       
            
            
        
   