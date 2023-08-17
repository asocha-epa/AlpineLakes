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

failed_downloads = []

#iterate through each of the returned items
for i in len(feat):
    item = feat[i]
    ID = item['id']
    QA = item['qa_pixel']
    QA_file = ID + "_QA_PIXEL.TIF"
    
    if 'lwir' in item:
        ST = item['lwir']
        ST_file = ID + "_ST_B6.TIF"
        
    if 'lwir11' in item:
        ST = item['lwir11']
        ST_file = ID + "_ST_B10.TIF"
        
    QA_link = QA['href']
    ST_link = ST['href']
    
    #check to see if the file is already downloaded before downloading
   folder = os.path.join(wd, ID))
    if not os.path.exists(folder):
        os.mkdir(folder)
    os.chdir(folder)
    if not os.path.exists(os.path.join(folder, QA_file)):
        try:
            print(f'downloading {QA_link}\n to {folder}\n')
            #send request for url to get content 
            r = requests.get(QA_link)
            with open(QA_file, 'wb') as f:
                f.write(r.content)
        except:
            print("download failed")
            failed_downloads.append(QA_link)
            
    if not os.path.exists(os.path.join(folder, ST_file)):
        try:
            print(f'downloading {ST_link}\n to {folder}\n')
            #send request for url to get content 
            r = requests.get(ST_link)
            with open(ST_file, 'wb') as f:
                f.write(r.content)
        except:
            print("download failed")
            failed_downloads.append(QA_link)
    break