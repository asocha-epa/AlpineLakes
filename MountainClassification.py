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

#read raster
landforms = rio.open(landforms_file)

#set buffer **make sure to check crs, for the AEA is used and its units are meters which is what we want
buffer = 1000

#copy df and buffer all geometries out to specified distance
buff_df = input_df
buff_df.geometry = buff_df.geometry.buffer(buffer)

#%%
for index, row in df.itterrows:
    ID = row['UNIQUE_ID']
    geom = row['geometry']