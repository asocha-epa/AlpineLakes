# -*- coding: utf-8 -*-
"""
Created on Thu Aug 17 09:07:07 2023

Testing out the STAC API that returns metadata for all landsat collections, which includes links for downloading

Using tutorital from USGS https://www.usgs.gov/media/files/landsat-stac-tutorial

@author: ASOCHA
"""
import requests 

stac = 'https://landsatlook.usgs.gov/stac-server'

stac_response = r.get(stac).json()   

catalog_links = stac_response['links']

params = {}

# create a list of bound box coordinates for area of interest
bbox = [-97.56546020507812,45.20332826663052,-97.2241973876953,45.52751668442124]

# assign bbox to the params dictionary
params['bbox'] = bbox

# use the specified datetime format to create string variable of desired time range
date_time = "2012-04-01T00:00:00Z/2012-05-01T23:59:59Z"

# add variable to params dictionary
params['datetime'] = date_time

# the collections parameter is a string object type. More than one ID can be passed in to the parameter by adding it to a list
collections = ['landsat-c2ard-st'] 

params['collections'] = collections

# add a new 'query' dictionary with the new parameters to the params dictionary
params['query'] = {'eo:cloud_cover':{'gte': 0, 'lt': 60}}

query = r.post(search, json=params).json() 

feat = query['features']

#iterate through each of the returned items
for i in len(feat):
    item = feat[i]
    ID = item['id']
    QA = item['qa_pixel']
    
    if 'lwir' in item:
        ST = item['lwir']
        
    if 'lwir11' in item:
        ST = item['lwir11']
        
    QA_link = QA['href']
    ST_link = ST['href']
    
    