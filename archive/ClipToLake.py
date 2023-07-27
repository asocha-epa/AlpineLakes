# -*- coding: utf-8 -*-
"""
Created on Wed Jul 26 09:07:35 2023

@author: ASOCHA

For analyzing surface temperature of lakes within a buffered region that delineates the lake - starts with buffering the lake area then
clipping the LST raster to the lake
"""
import geopandas as gpd
import rasterio as rio
from rasterio.mask import mask

# Reading in the input shapefile.
input_df = gpd.read_file(r'C:\Users\asocha\OneDrive - Environmental Protection Agency (EPA)\Profile\Documents\Alpine Lakes\Tahoe_Soils_and_Hydro_Data\Tahoe_Soils_and_Hydro_Data.shp')

# Reading the input CRS. 
input_crs = input_df.crs

# Reprojecting the data. If needed, substitute "WXYZ" with relevant EPSG code
#input_df = input_df.to_crs('epsg:WXYZ')

# Creating the variable-sized buffer
input_df['buffer'] = input_df.buffer(-100)

# Dropping the original geometry and setting the new geometry
buff_df = input_df.drop(columns=['geometry']).set_geometry('buffer')

# Reprojecting the buffered data back to the CRS used in the original input shapefile
buff_df = buff_df.to_crs(input_crs)

# Exporting the output to a shapefile
#buff_df.to_file(r'C:\Users\asocha\OneDrive - Environmental Protection Agency (EPA)\Profile\Documents\Alpine Lakes\Tahoe_Soils_and_Hydro_Data\Tahoe_Soils_and_Hydro_Data_100m_bufferIn.shp')

#%%
#read in the ST band and get its crs
src =  rio.open(r'D:\AlpineLakes\LandsatARD\1985\LT05_CU_003008_19850717_20210422_02_ST/LT05_CU_003008_19850717_20210422_02_ST_B6.TIF')
src_crs = src.crs

#project lake df to the same crs
buff_df = buff_df.to_crs(src.crs)

#from https://gist.github.com/mhweber/1af47ef361c3b20184455060945ac61b
def getFeatures(gdf):
    """Function to parse features from GeoDataFrame in such a manner that rasterio wants them"""
    import json
    return [json.loads(gdf.to_json())['features'][0]['geometry']]

coords = getFeatures(buff_df)

clipped_array, clipped_transform = mask(dataset=src, shapes=coords, crop=True)

out_meta = src.meta.copy()
out_meta.update({"driver": "GTiff",
                 "height": clipped_array.shape[1],
                 "width": clipped_array.shape[2],
                 "transform": clipped_transform})

out_tif= "clipped_example.tif"

with rio.open(out_tif, "w", **out_meta) as dest:
    dest.write(clipped_array)