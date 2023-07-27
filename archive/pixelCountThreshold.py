# -*- coding: utf-8 -*-
"""
Created on Mon Jul 10 12:03:55 2023

@author: ASOCHA

Check how much of raster is left within lake area after masking to remove any images that do not meet a specified threshold
"""

import rasterio as rio
import geopandas as gpd
import os
import tkinter as tk
from tkinter.filedialog import askdirectory
import numpy as np

root = tk.Tk()
root.withdraw()

#ask user to select folder for directory and set the wd
print('select folder', "\n")
wd = askdirectory(title = 'Select Directory Folder')
os.chdir(wd)

#iterate through files in the wd to get the original ST band and the masked ST band
for file in os.listdir(wd):
    if file.endswith('B6.TIF'):
        orig = rio.open(file).read()
    if file.endswith('mask.tif'):
        masked = rio.open(file).read()

#get the number of non zero pixels for each band
total_pix = np.count_nonzero(orig)
nonmasked_pix = np.count_nonzero(masked)

#find the proportion of masked pixels - if below threshold, do not use
percent = nonmasked_pix / total_pixels
print(percent)