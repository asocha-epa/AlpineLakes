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

#get rid of root window
root = tk.Tk()
root.withdraw()

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
                #get the QA and the surface temperature bands
                for file in os.listdir('.'):
                    if file.endswith('QA_PIXEL.TIF'):
                        QA_band = file
                    if file.endswith('ST_B10.TIF') or file.endswith('ST_B6.TIF'):
                        ST_band = file