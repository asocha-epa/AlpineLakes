# -*- coding: utf-8 -*-
"""
Created on Thu Jul 27 08:58:48 2023

Script to import as module for clipping rasters with shapefile using rasterio mask

@author: ASOCHA
"""
from rasterio.mask import mask

#from https://gist.github.com/mhweber/1af47ef361c3b20184455060945ac61b
def getFeatures(gdf):
    """Function to parse features from GeoDataFrame in such a manner that rasterio wants them"""
    import json
    return [json.loads(gdf.to_json())['features'][0]['geometry']]

def clipRaster(src, coords):
    clipped_array, clipped_transform = mask(dataset=src, shapes=coords, nodata = src.nodata, crop=True)
    out_meta = src.meta.copy()
    out_meta.update({"driver": "GTiff",
                 "height": clipped_array.shape[1],
                 "width": clipped_array.shape[2],
                 "transform": clipped_transform})
    return clipped_array, out_meta