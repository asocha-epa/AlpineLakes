# -*- coding: utf-8 -*-
"""
Created on Thu Jun 22 08:06:24 2023

@author: ASOCHA

Unpacking Landsat QA PIXEL band to mask clouds and other bad pixels from ST band
Uses script written by Conor O'Sullivan
https://towardsdatascience.com/removing-clouds-from-landsat-satellite-images-with-python-246e73494bc

Changed to use rasterio instead of tifffile for maintaining georeferencing

"""
import numpy as np
   
def get_mask(val,type='cloud'):
    
    #Get mask for a specific cover type

    # convert to binary
    bin_ = '{0:016b}'.format(val)

    # reverse string
    str_bin = str(bin_)[::-1]

    # get bit for cover type
    bits = {'cloud':3,'shadow':4,'dilated_cloud':1,'cirrus':2}
    bit = str_bin[bits[type]]

    if bit == '1':
        return 0 # cover
    else:
        return 1 # no cover

def mask_clouds(QA_band, ST_band):
    # Get masks
    cloud_mask = np.vectorize(get_mask)(QA_band,type='cloud')
    shadow_mask = np.vectorize(get_mask)(QA_band,type='shadow')
    dilated_cloud_mask = np.vectorize(get_mask)(QA_band,type='dilated_cloud')
    cirrus_mask = np.vectorize(get_mask)(QA_band,type='cirrus')

    # get mask for cloudy image
    mask = cloud_mask*shadow_mask*dilated_cloud_mask*cirrus_mask
    
    rmClouds = ST_band * mask
    
    return rmClouds

def cloud_mask(QA_band):
    # Get masks
    cloud_mask = np.vectorize(get_mask)(QA_band,type='cloud')
    shadow_mask = np.vectorize(get_mask)(QA_band,type='shadow')
    dilated_cloud_mask = np.vectorize(get_mask)(QA_band,type='dilated_cloud')
    cirrus_mask = np.vectorize(get_mask)(QA_band,type='cirrus')

    # get mask for cloudy image
    mask = cloud_mask*shadow_mask*dilated_cloud_mask*cirrus_mask
    
    return mask

