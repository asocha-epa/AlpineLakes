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
                  
for folder in os.listdir(wd):
    rootDir = os.path.join(wd, folder)
    for root, subDirs, files in os.walk(rootDir):
        for subDir in subDirs:
            newDir = os.path.join(rootDir, subDir)
            os.chdir(newDir)
            if subDir.endswith('.tar'):
                continue
            else: