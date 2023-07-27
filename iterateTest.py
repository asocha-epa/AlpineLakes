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

#get rid of root window
root = tk.Tk()
root.withdraw()

#read in shapefile - will need to update later for getting geometry from gpkg
input_df = gpd.read_file(r'C:\Users\asocha\OneDrive - Environmental Protection Agency (EPA)\Profile\Documents\Alpine Lakes\Tahoe_Soils_and_Hydro_Data\Tahoe_Soils_and_Hydro_Data.shp')

# Reading the input CRS. 
input_crs = input_df.crs

#reproject if necessary to match rasters which are Albers Equal Area
if input_crs != 'epsg:9822':
    input_df = input_df.to_crs('epsg:9822')

# Create buffer and set as new geometry
input_df['buffer'] = input_df.buffer(-100)
buff_df = input_df.drop(columns=['geometry']).set_geometry('buffer')

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
                        #read in raster bands as arrays
                        with rio.open(ST_band) as src:
                            surfTemp = src.read()
                            profile = src.profile
            
                        with rio.open(QA_band) as src:
                            QA = src.read()
                        
                        
            break
        break
    break