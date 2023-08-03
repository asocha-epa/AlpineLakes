# -*- coding: utf-8 -*-
"""
Created on Wed Aug  2 14:37:38 2023

Rewriting Amalia's mountain idenfication in python based on the USGS landforms categories

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
print('Setting working directory:', '\n', wd, '\n')
os.chdir(wd)

#get lake boundary file
lakes = askopenfilename(title = 'Select Lake Boundary File')
# Reading in the input file
input_df = gpd.read_file(lakes)

#get landforms file
landforms_file = askopenfilename(title = 'Select Landforms File')
#read raster
landforms = rio.open(landforms_file)

#set buffer
buffer = 1000

for i in input_df.index:
    