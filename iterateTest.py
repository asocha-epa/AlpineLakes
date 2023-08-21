# -*- coding: utf-8 -*-
"""
Created on Wed Jul 26 13:27:16 2023

@author: ASOCHA

Initial testing for combining lake temperature data processing in one script and iterating the process for all files downloaded
Working to make additional scripts into functions and modules that can be imported for a cleaner script
"""
import sys
import os
import tkinter as tk
from tkinter.filedialog import askdirectory, askopenfilename
import rasterio as rio
import geopandas as gpd
from rasterstats import zonal_stats
import numpy as np
import pandas as pd
import ClipToLake2
import landsatQAmask
import time
import shutil

#get starting time to get run time
st = time.time()

#get rid of root window
root = tk.Tk()
root.withdraw()

#make sure window comes to front
root.attributes('-topmost', 1)
#create function to apply scale factor and convert to degrees celcius
def tempToCelcius(val):
    return (val) * 0.00341802 + 149 - 273.15

#create empty lists to store values for creating a df
date = []
meanTemp_C = []
fifthPercentTemp_C = []
ninetyPercentTemp_C = []
tenthPercentTemp_C = []
ninetyfifthPercentTemp_C = []
year = []

#get lake boundary file
lakes = askopenfilename(title = 'Select Lake Boundary File')
# Reading in the input file
input_df = gpd.read_file(lakes)

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
    print(f'Processing {folder}\n')
    rootDir = os.path.join(wd, folder)
    for root, subDirs, files in os.walk(rootDir):
        for subDir in subDirs:
            newDir = os.path.join(rootDir, subDir)
            if subDir.endswith('.tar'):
                continue
            else:
                #get the QA and the surface temperature bands, save name for exporting files
                for file in os.listdir(newDir):
                    if file.endswith('QA_PIXEL.TIF'):
                        QA_band = os.path.join(newDir, file)
                    if file.endswith('ST_B10.TIF') or file.endswith('ST_B6.TIF'):
                        ST_band = os.path.join(newDir, file)
                        ST_name = file[:-4]
                        
                        #read in raster bands
                        try:
                            surf_temp = rio.open(ST_band)
                            ST_array = surf_temp.read(1)
                            profile = surf_temp.profile
                            affine = surf_temp.transform
                            nodata = surf_temp.nodata
                            
                            QA_pixel = rio.open(QA_band)
                            QA_array = QA_pixel.read(1)
                        except Exception as e:
                            print(e)
                            continue
                        
                        #project lake df to the same crs
                        buff_df = buff_df.to_crs(surf_temp.crs)
                        
                        #check if there is overlap with the rasters and the lake boundary
                        #run zonal stats to get the sum. the output is a dictionary in a list, so get that part by itself
                        #if sum is none, the areas don't intersect and the raster can be ignored
                        stats = zonal_stats(buff_df, ST_array, affine = affine, nodata = nodata, stats = 'sum')[0]
                        if stats['sum'] is None:
                            surf_temp.close()
                            QA_pixel.close()
                            shutil.rmtree(newDir)
                            continue
                        else:           
                            #run functions from ClipToLake2 script, **clipRaster output is a tuple with the array and the meta
                            coords = ClipToLake2.getFeatures(buff_df)
                           
                            QA_clip = ClipToLake2.clipRaster(QA_pixel, coords)
                            QA_clip_array = QA_clip[0]
                            
                            ST_clip = ClipToLake2.clipRaster(surf_temp, coords)
                            ST_clip_array = ST_clip[0]
                            ST_clip_meta = ST_clip[1]
                            
                            #mask out clouds using QA band with functions from landsatQAmask script
                            ST_masked = landsatQAmask.mask_clouds(QA_clip_array, ST_clip_array)
                              
                            #check how many pixels were masked, if below threshold, don't use
                            #get the number of non zero pixels for each band
                            total_pix = np.count_nonzero(ST_clip_array)
                            nonmasked_pix = np.count_nonzero(ST_masked)
                            percent = nonmasked_pix / total_pix
                            
                            if percent < 0.5: #need to establish a threshold here
                                surf_temp.close()
                                QA_pixel.close()
                                continue
                            else:
                                #set zeros as no data, need to convert to float array
                                ST_float = ST_masked.astype('float')
                                ST_float[ST_float == 0] = 'nan'
                                #apply scaling and conversion function
                                temp_cel = tempToCelcius(ST_float)

                                #change the raster dytpe to float to conserve decimals
                                ST_clip_meta.update(dtype=rio.float32)
                                
                                #write out final raster
                                out_file_name = ST_name + '_final_degCelcius.tif'
                                out_file = os.path.join(newDir, out_file_name)
                                if not os.path.exists(out_file):
                                    with rio.open(out_file, 'w', decimal_precision=4,  **ST_clip_meta) as dst:
                                        dst.write(temp_cel)
                            
                                #run zonal statistics on the ST raster within the lake boundary 
                                print(f'Running zonal stats on {file}\n')
                                stats = zonal_stats(buff_df, out_file, affine = affine, nodata = nodata, stats = 'mean  percentile_5 percentile_10 percentile_90 percentile_95')[0]

                                #get values and store them in the empty lists
                                nameSplit = ST_name.split('_')
                                fileDate = nameSplit[3]
                                date.append(fileDate)
                                year.append(folder)

                                fifthPercentTemp_C.append(stats['percentile_5'])
                                ninetyPercentTemp_C.append(stats['percentile_90'])
                                tenthPercentTemp_C.append(stats['percentile_10'])
                                meanTemp_C.append(stats['mean'])
                                ninetyfifthPercentTemp_C.append(stats['percentile_95'])
                                
                                surf_temp.close()
                                QA_pixel.close()
                                
#create dataframe with dates and the statistics for each date
df = pd.DataFrame(zip(date, year, fifthPercentTemp_C,tenthPercentTemp_C, meanTemp_C,  ninetyPercentTemp_C,  ninetyfifthPercentTemp_C),
                  columns = ['date', 'year', 'fifthPercentTemp_C', 'tenthPercentTemp_C', 'meanTemp_C', 'ninetyPercentTemp_C', 'ninetyfifth%Temp_C'])

print(df.head())
#%%
df.to_csv(r'C:\Users\ASOCHA\OneDrive - Environmental Protection Agency (EPA)\Profile\Documents\Alpine Lakes\FlatheadTestRun_Threshold50.csv')                          

#get run time
et = time.time()
res = et - st
final_res = res / 60
print('Execution time:', final_res, 'minutes')                       
         
           
        

                       
            
            
        
   