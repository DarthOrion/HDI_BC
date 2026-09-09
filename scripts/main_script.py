# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 12:21:39 2021

@author: marias
"""

from pathlib import Path
import os
import site
import sys
import numpy as np
import rasterio
from osgeo import gdal

gdal.UseExceptions()

# =============================================================================
# Project Directory Setup
# =============================================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
SCRIPTS_DIR = BASE_DIR / "scripts"

# Add custom scripts directory to Python path
site.addsitedir(str(SCRIPTS_DIR))
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.append(str(SCRIPTS_DIR))

from raster_functions import (
    rasterize, 
    rasterize_all, 
    proximity_raster, 
    score_raster, 
    score_raste_water, 
    normalize, 
    reduction, 
    delete_files_in_directory
)

# Base Map Reference
base_layer = str(DATA_DIR / "base_maps" / "BC_Terrestrial_Map_Float.tif")

# Main output directory for individual pressure rasters
PRESSURES_DIR = OUTPUT_DIR / "Human_Pressures"
PRESSURES_DIR.mkdir(parents=True, exist_ok=True)

# =============================================================================
# Roads
# =============================================================================

input_roads = DATA_DIR / "Roads"
out_folder_roads = OUTPUT_DIR / "Roads"
out_folder_roads.mkdir(parents=True, exist_ok=True)

shapedir = [str(input_roads / f) for f in os.listdir(input_roads) if f.endswith('.shp')]

for shape in shapedir:
    rasterize(base_layer, str(out_folder_roads), shape)

# Proximity maps
input_raster = str(out_folder_roads)
out_prox = str(out_folder_roads / "Proximity_maps")

rasterdir = [str(Path(input_raster) / f) for f in os.listdir(input_raster) if f.endswith('.tif')]

for map_ras in rasterdir:
    proximity_raster(map_ras, out_prox)

# Exponential and Scored maps
input_prox = str(out_folder_roads / "Proximity_maps")
out_fuzzy = str(out_folder_roads / "Scored")

prox_dir = [str(Path(input_prox) / f) for f in os.listdir(input_prox) if f.endswith('.tif')]

scale_factors = [8, 6, 3, 2]
direct = [60, 30, 10, 10]
indirect = [5000, 2500, 1000, 500]
atenuation_factor = [600, 600, 300, 300]

for ras_input, sf, d, i, at in zip(prox_dir, scale_factors, direct, indirect, atenuation_factor):
    score_raster(ras_input, out_fuzzy, sf, d, i, at)

# Merge Rasters
input_merge = str(out_folder_roads / "Scored")
out_merge = str(PRESSURES_DIR / "Road_pressures.tif")

merge_dir = [str(Path(input_merge) / f) for f in os.listdir(input_merge) if f.endswith('.tif')]

map2array = []
for raster in merge_dir:
    with rasterio.open(raster) as src:
        map2array.append(src.read().astype(np.float32))
        profile = src.profile
 
mosaic = np.fmax.reduce(map2array, initial=np.nan)

with rasterio.open(out_merge, 'w', **profile) as dst:
    dst.write(mosaic)

del map2array, mosaic
delete_files_in_directory(input_prox)

print("Roads 100%")

# =============================================================================
# Navigable Waterways
# =============================================================================

input_nav = DATA_DIR / "Accessibility" / "Navigable_Waterways"
out_folder_nav = OUTPUT_DIR / "Navigable_Waterways"
out_folder_nav.mkdir(parents=True, exist_ok=True)

shapedir = [str(input_nav / f) for f in os.listdir(input_nav) if f.endswith('.shp')]

for shape in shapedir:
    rasterize(base_layer, str(out_folder_nav), shape)

# Proximity maps
input_raster = str(out_folder_nav)
out_prox = str(out_folder_nav / "Proximity_maps")

rasterdir = [str(Path(input_raster) / f) for f in os.listdir(input_raster) if f.endswith('.tif')]

for map_ras in rasterdir:
    proximity_raster(map_ras, out_prox)

# Exponential and Scored maps
input_prox = str(out_folder_nav / "Proximity_maps")
out_fuzzy = str(out_folder_nav / "Scored")

prox_dir = [str(Path(input_prox) / f) for f in os.listdir(input_prox) if f.endswith('.tif')]

scale_factors = [2, 4]
direct = [10, 10]
indirect = [500, 500]
atenuation_factor = [300, 300]

for ras_input, sf, d, i, at in zip(prox_dir, scale_factors, direct, indirect, atenuation_factor):
    score_raste_water(ras_input, out_fuzzy, sf, d, i, at)

# Merge Rasters
input_merge = str(out_folder_nav / "Scored")
out_merge = str(PRESSURES_DIR / "waterways_pressures.tif")

merge_dir = [str(Path(input_merge) / f) for f in os.listdir(input_merge) if f.endswith('.tif')]

map2array = []
for raster in merge_dir:
    with rasterio.open(raster) as src:
        map2array.append(src.read().astype(np.float32))
        profile = src.profile

mosaic = np.fmax.reduce(map2array, initial=np.nan)

with rasterio.open(base_layer) as src:
    mask = src.read().astype(np.float32)

mosaic1 = mask * mosaic
mosaic1[np.where(mosaic1 == 0)] = np.nan

with rasterio.open(out_merge, 'w', **profile) as dst:
    dst.write(mosaic1)

del map2array, mosaic, mosaic1
delete_files_in_directory(input_merge)
delete_files_in_directory(input_prox)

print("Navigable Waterways 100%")

# =============================================================================
# Railways
# =============================================================================

input_rail = DATA_DIR / "Accessibility" / "Railways"
out_folder_rail = OUTPUT_DIR / "Railways"
out_folder_rail.mkdir(parents=True, exist_ok=True)

shapedir = [str(input_rail / f) for f in os.listdir(input_rail) if f.endswith('.shp')]

for shape in shapedir:
    rasterize(base_layer, str(out_folder_rail), shape)

# Proximity maps
input_raster = str(out_folder_rail)
out_prox = str(out_folder_rail / "Proximity_maps")

rasterdir = [str(Path(input_raster) / f) for f in os.listdir(input_raster) if f.endswith('.tif')]

for map_ras in rasterdir:
    proximity_raster(map_ras, out_prox)

# Exponential and Scored maps
input_prox = str(out_folder_rail / "Proximity_maps")
out_fuzzy = str(PRESSURES_DIR)

prox_dir = [str(Path(input_prox) / f) for f in os.listdir(input_prox) if f.endswith('.tif')]

scale_factors = [8]
direct = [31]
indirect = [500]
atenuation_factor = [150]

for ras_input, sf, d, i, at in zip(prox_dir, scale_factors, direct, indirect, atenuation_factor):
    score_raster(ras_input, out_fuzzy, sf, d, i, at)

delete_files_in_directory(input_prox)
print("Railways 100%")

# =============================================================================
# Linear Features
# =============================================================================

# Updated path to point directly inside data/
input_lf = DATA_DIR / "Linear_Features"
out_folder_lf = OUTPUT_DIR / "Linear_Features"
out_folder_lf.mkdir(parents=True, exist_ok=True)

shapedir = [str(input_lf / f) for f in os.listdir(input_lf) if f.endswith('.shp')]

seismic_file = str(input_lf / "Seismic_Lines_pol.shp")
if seismic_file in shapedir:
    shapedir.remove(seismic_file)

for shape in shapedir:
    rasterize(base_layer, str(out_folder_lf), shape)

# Proximity maps
input_raster = str(out_folder_lf)
out_prox = str(out_folder_lf / "Proximity_maps")

rasterdir = [str(Path(input_raster) / f) for f in os.listdir(input_raster) if f.endswith('.tif')]

for map_ras in rasterdir:
    proximity_raster(map_ras, out_prox)

# Exponential and Scored maps
input_prox = str(out_folder_lf / "Proximity_maps")
out_fuzzy = str(PRESSURES_DIR)

prox_dir = [str(Path(input_prox) / f) for f in os.listdir(input_prox) if f.endswith('.tif')]

scale_factors = [3, 2, 3]
direct = [5, 5, 30]
indirect = [2500, 500, 1000]
atenuation_factor = [300, 300, 300]

for ras_input, sf, d, i, at in zip(prox_dir, scale_factors, direct, indirect, atenuation_factor):
    score_raster(ras_input, out_fuzzy, sf, d, i, at)

delete_files_in_directory(input_prox)
print("Linear Features 100%")

# =============================================================================
# Dams and Reservoirs
# =============================================================================

input_dams = DATA_DIR / "Energy"
out_folder_dams = OUTPUT_DIR / "Dams_and_Reservoirs"
out_folder_dams.mkdir(parents=True, exist_ok=True)

shapedir = [str(input_dams / f) for f in os.listdir(input_dams) if f.endswith('.shp')]

for shape in shapedir:
    rasterize(base_layer, str(out_folder_dams), shape)

# Proximity maps
input_raster = str(out_folder_dams)
out_prox = str(out_folder_dams / "Proximity_maps")

rasterdir = [str(Path(input_raster) / f) for f in os.listdir(input_raster) if f.endswith('.tif')]

for map_ras in rasterdir:
    proximity_raster(map_ras, out_prox)

# Exponential and Scored maps
input_prox = str(out_folder_dams / "Proximity_maps")
out_fuzzy = str(out_folder_dams / "Scored")

prox_dir = [str(Path(input_prox) / f) for f in os.listdir(input_prox) if f.endswith('.tif')]

dams = prox_dir[0]
reservoirs = prox_dir[1]

score_raster(dams, out_fuzzy, 10, 30, 100, 100)
score_raste_water(reservoirs, out_fuzzy, 6, 30, 500, 300)

# Merge Rasters
input_merge = str(out_folder_dams / "Scored")
out_merge = str(PRESSURES_DIR / "Dams_Reservoirs.tif")

merge_dir = [str(Path(input_merge) / f) for f in os.listdir(input_merge) if f.endswith('.tif')]

map2array = []
for raster in merge_dir:
    with rasterio.open(raster) as src:
        map2array.append(src.read().astype(np.float32))
        profile = src.profile

mosaic = np.fmax.reduce(map2array, initial=np.nan)

with rasterio.open(out_merge, 'w', **profile) as dst:
    dst.write(mosaic)

del map2array, mosaic
delete_files_in_directory(input_prox)
delete_files_in_directory(input_merge)

print("Dams and reservoirs 100%")

# =============================================================================
# Land Use
# =============================================================================

input_land = DATA_DIR / "LandUse"
out_folder_land = str(PRESSURES_DIR)

shapedir = [str(input_land / f) for f in os.listdir(input_land) if f.endswith('.shp')]

for shape in shapedir:
    rasterize(base_layer, out_folder_land, shape)

print("Landuse 100%")

# Crops and Pastures Reclassification
input_land_raster = str(DATA_DIR / "LandUse" / "aci_2021_bc_clipped.tif")

crops_values = {
    10: np.nan, 20: np.nan, 30: np.nan, 34: np.nan, 35: np.nan, 50: np.nan, 80: np.nan, 85: np.nan,
    110: np.nan, 120: 7, 122: np.nan, 130: 7, 131: 7, 132: 7, 133: 7, 134: 7, 135: 7,
    136: 7, 137: 7, 138: 7, 139: 7, 140: 7, 141: 7, 142: 7, 143: 7, 145: 7,
    146: 7, 147: 7, 148: 7, 149: 7, 150: 7, 151: 7, 152: 7, 153: 7, 154: 7,
    155: 7, 156: 7, 157: 7, 158: 7, 160: 7, 161: 7, 162: 7, 163: 7, 167: 7,
    168: 7, 174: 7, 175: 7, 176: 7, 177: 7, 178: 7, 179: 7, 180: 7, 181: 7,
    182: 7, 183: 7, 185: 7, 188: 7, 189: 7, 190: 7, 191: 7, 192: 7, 193: 7,
    194: 7, 195: 7, 196: 7, 197: 7, 198: 7, 199: 7, 200: np.nan, 210: np.nan,
    220: np.nan, 230: np.nan, 0: np.nan
}

pastures_values = {
    10: np.nan, 20: np.nan, 30: np.nan, 34: np.nan, 35: np.nan, 50: np.nan, 80: np.nan, 85: np.nan,
    110: np.nan, 120: np.nan, 122: 5, 130: np.nan, 131: np.nan, 132: np.nan, 133: np.nan, 134: np.nan, 135: np.nan,
    136: np.nan, 137: np.nan, 138: np.nan, 139: np.nan, 140: np.nan, 141: np.nan, 142: np.nan, 143: np.nan, 145: np.nan,
    146: np.nan, 147: np.nan, 148: np.nan, 149: np.nan, 150: np.nan, 151: np.nan, 152: np.nan, 153: np.nan, 154: np.nan,
    155: np.nan, 156: np.nan, 157: np.nan, 158: np.nan, 160: np.nan, 161: np.nan, 162: np.nan, 163: np.nan, 167: np.nan,
    168: np.nan, 174: np.nan, 175: np.nan, 176: np.nan, 177: np.nan, 178: np.nan, 179: np.nan, 180: np.nan, 181: np.nan,
    182: np.nan, 183: np.nan, 185: np.nan, 188: np.nan, 189: np.nan, 190: np.nan, 191: np.nan, 192: np.nan, 193: np.nan,
    194: np.nan, 195: np.nan, 196: np.nan, 197: np.nan, 198: np.nan, 199: np.nan, 200: np.nan, 210: np.nan,
    220: np.nan, 230: np.nan, 0: np.nan
}

with rasterio.open(input_land_raster) as src:
    input_data = src.read(1)
    
    crops_data = np.vectorize(crops_values.get)(input_data)
    pastures_data = np.vectorize(pastures_values.get)(input_data)

    output_crops_path = PRESSURES_DIR / "Agriculture.tif"
    profile = src.profile.copy()
    profile.update(dtype=rasterio.float32)
    
    with rasterio.open(output_crops_path, 'w', **profile) as dst_crops:
        dst_crops.write(crops_data, 1)

    output_pastures_path = PRESSURES_DIR / "Pastures_data.tif"
    with rasterio.open(output_pastures_path, 'w', **profile) as dst_pastures:
        dst_pastures.write(pastures_data, 1)

del crops_data, crops_values, input_data, pastures_data, pastures_values
print("Crops and Pastures: 100%.")

# =============================================================================
# Population Density
# =============================================================================

input_popdens = str(DATA_DIR / "Pop_density" / "Pop_density_2021.shp")
pop_density_out_dir = str(OUTPUT_DIR / "Pop_Density")
Path(pop_density_out_dir).mkdir(parents=True, exist_ok=True)

rasterize(base_layer, pop_density_out_dir, input_popdens)

pop_density = str(Path(pop_density_out_dir) / "Pop_density_2021_raster.tif")
pop_density_out = str(PRESSURES_DIR / "Pop_density.tif")

with rasterio.open(pop_density) as src:
    map2array = src.read().astype(np.float32)
    profile = src.profile
        
    log_map = np.log(map2array + 1)
    norm_map = normalize(log_map, 0, 10)
    norm_map[np.where(norm_map < 1)] = np.nan

with rasterio.open(pop_density_out, 'w', **profile) as dst:
    dst.write(norm_map)

print("Pop Density 100%")

# =============================================================================
# Buildings
# =============================================================================

input_buildings = str(DATA_DIR / "Build_up_areas" / "Buildings.shp")
out_buildings = str(PRESSURES_DIR)

rasterize_all(base_layer, out_buildings, input_buildings)
print("Buildings 100%")

# =============================================================================
# Oil & Gas
# =============================================================================

input_oil_gas = DATA_DIR / "O&G"
out_oil_gas = OUTPUT_DIR / "Oil&Gas"
out_oil_gas.mkdir(parents=True, exist_ok=True)

shapedir = [str(input_oil_gas / f) for f in os.listdir(input_oil_gas) if f.endswith('.shp')]

for shape in shapedir:
    rasterize(base_layer, str(out_oil_gas), shape)

# Merge Rasters
input_merge = str(out_oil_gas)
out_merge = str(PRESSURES_DIR / "Oil_Gas.tif")

merge_dir = [str(Path(input_merge) / f) for f in os.listdir(input_merge) if f.endswith('.tif')]

map2array = []
for raster in merge_dir:
    with rasterio.open(raster) as src:
        map2array.append(src.read().astype(np.float32))
        profile = src.profile

mosaic = np.fmax.reduce(map2array, initial=np.nan)

with rasterio.open(out_merge, 'w', **profile) as dst:
    dst.write(mosaic)

del map2array, mosaic
print("Oil_Wells 100%")

# =============================================================================
# Recreation
# =============================================================================

input_recreation = DATA_DIR / "Recreation"
out_recreation = OUTPUT_DIR / "Recreation"
out_recreation.mkdir(parents=True, exist_ok=True)

shapedir = [str(input_recreation / f) for f in os.listdir(input_recreation) if f.endswith('.shp')]

for shape in shapedir:
    rasterize(base_layer, str(out_recreation), shape)

# Proximity maps
input_raster = str(out_recreation)
out_prox = str(out_recreation / "Proximity_maps")

rasterdir = [str(Path(input_raster) / f) for f in os.listdir(input_raster) if f.endswith('.tif')]
rasterdir.pop(2)  # Recreation sites dropped as it is a polygon layer

for map_ras in rasterdir:
    proximity_raster(map_ras, out_prox)

# Exponential and Scored maps
input_prox = str(out_recreation / "Proximity_maps")
out_fuzzy = str(out_recreation / "Scored")

prox_dir = [str(Path(input_prox) / f) for f in os.listdir(input_prox) if f.endswith('.tif')]

lakes = prox_dir.pop(1)

scale_factors = [1.5, 0.9]
direct = [30, 30]
indirect = [100, 100]
atenuation_factor = [100, 100]

for ras_input, sf, d, i, at in zip(prox_dir, scale_factors, direct, indirect, atenuation_factor):
    score_raster(ras_input, out_fuzzy, sf, d, i, at)

score_raste_water(lakes, out_fuzzy, 2, 5, 100, 100)

# Merge Rasters
input_merge = str(out_recreation / "Scored")
out_merge = str(PRESSURES_DIR / "Recreation.tif")
recre_sites = str(out_recreation / "Recreation_sites_raster.tif")

merge_dir = [str(Path(input_merge) / f) for f in os.listdir(input_merge) if f.endswith('.tif')]
merge_dir.append(recre_sites)

map2array = []
for raster in merge_dir:
    with rasterio.open(raster) as src:
        map2array.append(src.read().astype(np.float32))
        profile = src.profile

mosaic = np.fmax.reduce(map2array, initial=np.nan)

with rasterio.open(out_merge, 'w', **profile) as dst:
    dst.write(mosaic)

del map2array, mosaic
delete_files_in_directory(input_prox)
delete_files_in_directory(input_merge)

print("Recreation 100%")

# =============================================================================
# Reduce File Sizes
# =============================================================================

input_files = str(PRESSURES_DIR)
output_files = str(OUTPUT_DIR / "Human_Pressures2")

rasterdir = [str(Path(input_files) / f) for f in os.listdir(input_files) if f.endswith('.tif')]

for rasterfile in rasterdir:
    reduction(rasterfile, output_files)

print("Reducing files size 100%")

# =============================================================================
# Aggregate Human Disturbance Index (HDI)
# =============================================================================

input_pressures = str(PRESSURES_DIR)
output_HDI = str(OUTPUT_DIR / "BC_HDI" / "BC_HDI.tif")
Path(output_HDI).parent.mkdir(parents=True, exist_ok=True)

with rasterio.open(base_layer) as src:
    mask = src.read().astype(np.float32)

merge_dir = [str(Path(input_pressures) / f) for f in os.listdir(input_pressures) if f.endswith('.tif')]

sum_array = None

for layer in merge_dir:
    with rasterio.open(layer) as src:
        layer_data = src.read().astype(np.float32)
        layer_data = np.nan_to_num(layer_data)
        
        if sum_array is None:
            sum_array = layer_data
        else:
            sum_array += layer_data

sum_array = np.round(sum_array, 3)
sum_array_zeros = np.nan_to_num(sum_array)
HDI = np.where(mask == 1, sum_array_zeros, np.nan)

with rasterio.open(merge_dir[0]) as src:
    profile = src.profile
    profile.update(compress='lzw', nodata=None)

with rasterio.open(output_HDI, 'w', **profile) as dst:
    dst.write(HDI)

print("HDI Mapping Complete.")