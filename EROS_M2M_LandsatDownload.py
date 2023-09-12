# -*- coding: utf-8 -*-
"""
Created on Wed Jul 26 09:07:35 2023

@author: ASOCHA

Building on a sample script provided by the USGS for downloading data from their M2M API to download landsat

original: https://m2m.cr.usgs.gov/api/docs/example/download_data-py
"""
# =============================================================================
#  USGS/EROS Inventory Service Example
#  Python - JSON API
# 
#  Script Last Modified: 2/15/2023
#  Note: This example does not include any error handling!
#        Any request can throw an error, which can be found in the errorCode proprty of
#        the response (errorCode, errorMessage, and data properies are included in all responses).
#        These types of checks could be done by writing a wrapper similiar to the sendRequest function below
#  Usage: python download_data.py -u username -p password
# =============================================================================

import json
import requests
import sys
import time
import geopandas as gpd
import os
from urllib.parse import urlparse
import tarfile
import tkinter as tk
from tkinter.filedialog import askdirectory, askopenfilename
import time
import certifi

#get rid of root window
root = tk.Tk()
root.withdraw()

#make sure window comes to front
root.attributes('-topmost', 1)

#get working directory path
print('select download destination folder', "\n")
wd = askdirectory(title = 'Select Directory Folder')

#set working directory
os.chdir(wd)

#get lake boundary file
print('select lake boundary file', "\n")
lakes = askopenfilename(title = 'Select Lake Boundary File')

#get starting time to get run time
st = time.time()

#%%
#read in lake boundary file, convert to wgs84, and get bounding box values for running search
shp = gpd.read_file(lakes)
shp_wgs84 = shp.to_crs(epsg = 4326)
minx = round(shp_wgs84.total_bounds[0], 4)
miny = round(shp_wgs84.total_bounds[1], 4)
maxx =round(shp_wgs84.total_bounds[2], 4)
maxy = round(shp_wgs84.total_bounds[3], 4)

# send http request - from original
def sendRequest(url, data, apiKey = None):  
    json_data = json.dumps(data)
    
    if apiKey == None:
        #needed to add a server certificate verification bc randomly started not being able to verify it
        response = requests.post(url, json_data, verify = certifi.where())
    else:
        headers = {'X-Auth-Token': apiKey}              
        response = requests.post(url, json_data, headers = headers, verify = certifi.where())    
    
    try:
      httpStatusCode = response.status_code 
      if response == None:
          print("No output from service")
          sys.exit()
      output = json.loads(response.text)	
      if output['errorCode'] != None:
          print(output['errorCode'], "- ", output['errorMessage'])
          #added to handle download request limit by waiting 15 min to continue
          if output['errorCode'] == 'RATE_LIMIT_USER_DL':
              print('Waiting 15 minutes to retry download...')
              time.sleep(900)
          else:
             sys.exit()
          sys.exit()
      if  httpStatusCode == 404:
          print("404 Not Found")
          sys.exit()
      elif httpStatusCode == 401: 
          print("401 Unauthorized")
          sys.exit()
      elif httpStatusCode == 400:
          print("Error Code", httpStatusCode)
          sys.exit()
    except Exception as e: 
          response.close()
          print(e)
          sys.exit()
    response.close()
    
    return output['data']


if __name__ == '__main__': 
    
    # **CHANGED HERE use token instead of password and got rid of the arguments for now 
    #if you want to use password, see original script linked at the top
    username = 'INSERT USERNAME HERE'
    token = 'INSERT TOKEN HERE'     

    print("\nRunning Scripts...\n")
    
    serviceUrl = "https://m2m.cr.usgs.gov/api/api/json/stable/"
    
    # login
    payload = {'username' : username, 'token' : token}
   
    apiKey = sendRequest(serviceUrl + "login-token", payload)
    
    print("API Key: " + apiKey + "\n")
    
    datasetName = "ard_tile"   #analysis ready data tiles
    
    #use bbox from lake for spatial search
    spatialFilter =  {'filterType' : "mbr",
                      'lowerLeft' : {'latitude' : miny, 'longitude' : minx},
                      'upperRight' : { 'latitude' : maxy, 'longitude' : maxx}}
                     
    temporalFilter = {'start' : '1982-01-10', 'end' : '2022-12-10'}
    
    payload = {'datasetName' : datasetName,
                               'spatialFilter' : spatialFilter,
                               'temporalFilter' : temporalFilter}                     
    
    print("Searching datasets...\n")
    datasets = sendRequest(serviceUrl + "dataset-search", payload, apiKey)
    
    print("Found ", len(datasets), " datasets\n")
    
    # download datasets
    for dataset in datasets:
        #had issue with not doing every year, so made it an iteration through years of interest
        for i in range(1983,2023):
            #filter by desired aquisition dates, here I used summer months only
            acquisitionFilter = {"end": f"{i}-09-31",
                                     "start": f"{i}-06-01" }        
            #add in cloud cover percentage filter    
            payload = {'datasetName' : dataset['datasetAlias'], 
                                    # 'maxResults' : 2,
                                    # 'startingNumber' : 1, 
                                     'sceneFilter' : { 'cloudCoverFilter' : {"min": 0, "max": 10},
                                                      'spatialFilter' : spatialFilter,
                                                      'acquisitionFilter' : acquisitionFilter}}
            
            # Now I need to run a scene search to find data to download
            print("Searching scenes...\n\n")   
            
            scenes = sendRequest(serviceUrl + "scene-search", payload, apiKey)
        
            # Did we find anything?
            if scenes['recordsReturned'] > 0:
                # Aggregate a list of scene ids
                sceneIds = []
                for result in scenes['results']:
                    # Add this scene to the list I would like to download
                    sceneIds.append(result['entityId'])
                
                # Find the download options for these scenes
                # NOTE :: Remember the scene list cannot exceed 50,000 items!
                payload = {'datasetName' : dataset['datasetAlias'], 'entityIds' : sceneIds}
                                    
                downloadOptions = sendRequest(serviceUrl + "download-options", payload, apiKey)
            
                # Aggregate a list of available products
                downloads = []
                for product in downloadOptions:
                        # Make sure the product is available for this scene
                        if product['available'] == True:
                             downloads.append({'entityId' : product['entityId'],
                                               'productId' : product['id']})
                             
                # Did we find products?
                if downloads:
                    requestedDownloadsCount = len(downloads)
                    # set a label for the download request
                    label = "download-sample"
                    payload = {'downloads' : downloads,
                                                 'label' : label}
                    # Call the download to get the direct download urls
                    requestResults = sendRequest(serviceUrl + "download-request", payload, apiKey)          
                                  
                    # PreparingDownloads has a valid link that can be used but data may not be immediately available
                    # Call the download-retrieve method to get download that is available for immediate download
                    if requestResults['preparingDownloads'] != None and len(requestResults['preparingDownloads']) > 0:
                        payload = {'label' : label}
                        moreDownloadUrls = sendRequest(serviceUrl + "download-retrieve", payload, apiKey)
                        
                        downloadIds = []  
                        
                        for download in moreDownloadUrls['available']:
                            if str(download['downloadId']) in requestResults['newRecords'] or str(download['downloadId']) in requestResults['duplicateProducts']:
                                downloadIds.append(download['downloadId'])
                                print("DOWNLOAD: " + download['url'])
                            
                        for download in moreDownloadUrls['requested']:
                            if str(download['downloadId']) in requestResults['newRecords'] or str(download['downloadId']) in requestResults['duplicateProducts']:
                                downloadIds.append(download['downloadId'])
                                print("DOWNLOAD: " + download['url'])
                         
                        # Didn't get all of the reuested downloads, call the download-retrieve method again probably after 30 seconds
                        while len(downloadIds) < (requestedDownloadsCount - len(requestResults['failed'])): 
                            preparingDownloads = requestedDownloadsCount - len(downloadIds) - len(requestResults['failed'])
                            print("\n", preparingDownloads, "downloads are not available. Waiting for 30 seconds.\n")
                            time.sleep(30)
                            print("Trying to retrieve data\n")
                            moreDownloadUrls = sendRequest(serviceUrl + "download-retrieve", payload, apiKey)
                            for download in moreDownloadUrls['available']:                            
                                if download['downloadId'] not in downloadIds and (str(download['downloadId']) in requestResults['newRecords'] or str(download['downloadId']) in requestResults['duplicateProducts']):
                                    downloadIds.append(download['downloadId'])
                                    print("DOWNLOAD: " + download['url']) 
                                
                    else:
                        # Get all available downloads
                        for download in requestResults['availableDownloads']:
                           #create list to keep on urls that fail
                            failedDownloads = []
                            url = download['url']
                            #parse the url into separate pieces to pull information from
                            parse = urlparse(url)
                            #get the scene name
                            name = parse[4].split('&')[0].split('=')[1]
                            #split the scene name into parts
                            nameSplit = name.split('_')
                            #get the date from the name to filter by month (the fourth item in the list from splitting the name)
                            #check list length bc there are some with just an 'frbj' in them and don't want to use them
                            if len(nameSplit) > 4:
                                #get the surface temperature bands
                                if nameSplit[-1] == 'ST': 
                                    #create tar file name for downloading
                                    file = name + '.tar'  
                                    print(file)
                                    #check to see if the file is already downloaded before downloading
                                    yearFolder = os.path.join(wd, str(i))
                                    if not os.path.exists(yearFolder):
                                        os.mkdir(yearFolder)
                                    os.chdir(yearFolder)
                                    if not os.path.exists(os.path.join(yearFolder, file)):
                                        #try downloading the file from the url, if it doesn't work, add the url to a list
                                        try:
                                            print(f'downloading {url}\n to {yearFolder}\n')
                                            #send request for url to get content 
                                            r = requests.get(url, timeout = 300)
                                            with open(file, 'wb') as f:
                                                f.write(r.content)
                                        except:
                                            print("download failed")
                                            failedDownloads.append(url)
                                            pass
                                        
                    print("\nAll downloads are available to download.\n")
            else:
                print("Search found no results.\n")
                

        
#%%#        
#Added to unzip to downloaded zip files into folders of the same name
failed_unzip = []
for root, dirs, files in os.walk(wd):
    for file in files:
        if file.endswith('.tar'):
             sensor = file.split('.')[0]
             sensorFolder = os.path.join(root, sensor)
             if not os.path.exists(sensorFolder):
                 os.mkdir(sensorFolder)
             try:
                 file = tarfile.open(os.path.join(root, file))
                 # extracting file
                
                 file.extractall(sensorFolder)
                  
                 file.close()
             except:
                failed_unzip.append(sensor)
                pass

#retry the files that failed to unzip
if len(failed_unzip) > 0:
    url = 'https://landsatlook.usgs.gov/gen-bundle?landsat_product_id='
    for file in failed_unzip:
        name = file.split('.')[0]
        year = name.split('_')[3][:4]
        os.chdir(os.path.join(wd, year))
        fullURL = url + str(name) 
        r = requests.get(url)
        with open(file, 'wb') as f:
            f.write(r.content)
            f.close()

#delete the tar files after they have been unzipped
for root, dirs, files in os.walk(wd):
    for file in files:
        if file.endswith('.tar'):
            os.remove(os.path.join(root, file))

#get run time
et = time.time()
res = et - st
final_res = res / 60
print('Execution time:', final_res, 'minutes')

# Logout so the API Key cannot be used anymore
endpoint = "logout"  
if sendRequest(serviceUrl + endpoint, None, apiKey) == None:        
    print("Logged Out\n\n")
else:
    print("Logout Failed\n\n")