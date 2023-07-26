# -*- coding: utf-8 -*-
"""
Created on Wed Jul 26 09:07:35 2023

@author: ASOCHA

For analyzing surface temperature of lakes within a buffered region that delineates the lake - starts with buffering the lake area then
clipping the LST raster to the lake
"""
import geopandas as gpd

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