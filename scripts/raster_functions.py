# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 14:05:04 2021

@author: marias
"""
import os
import glob
import fnmatch
import numpy as np
import geopandas as gpd
import rasterio
from rasterio import features
from rasterio.merge import merge
from rasterio.plot import show
from rasterio.crs import CRS
from osgeo import gdal, ogr, osr
from pathlib import Path


def rasterize(base_layer, out_folder, input_shp):
    out_folder = Path(out_folder)
    out_folder.mkdir(parents=True, exist_ok=True)
    
    input_shp = Path(input_shp)
    outputlayer = out_folder / f"{input_shp.stem}_raster.tif"

    shaperead = gpd.read_file(input_shp)
    
    if "PROJECT" in shaperead.columns:
        shapes = ((geom, val) for geom, val in zip(shaperead.geometry, shaperead.PROJECT))
    else:
        shapes = ((geom, 1) for geom in shaperead.geometry)

    # Read base layer dimensions and transform in read mode
    with rasterio.open(base_layer, 'r') as rst:
        meta = rst.meta.copy()
        transform = rst.transform
        height = rst.height
        width = rst.width

    meta.update(compress='lzw', dtype=rasterio.float32, count=1)

    # Initialize empty array in memory
    out_arr = np.zeros((height, width), dtype=np.float32)
    burned = features.rasterize(shapes=shapes, fill=0, out=out_arr, transform=transform)

    # Write array to the target output layer
    with rasterio.open(outputlayer, 'w', **meta) as out:
        out.write(burned, 1)


def rasterize_all(base_layer, out_folder, input_shp):
    out_folder = Path(out_folder)
    out_folder.mkdir(parents=True, exist_ok=True)
    
    input_shp = Path(input_shp)
    outputlayer = out_folder / f"{input_shp.stem}_raster.tif"

    shaperead = gpd.read_file(input_shp)

    if "PROJECT" in shaperead.columns:
        shapes = ((geom, val) for geom, val in zip(shaperead.geometry, shaperead.PROJECT))
    else:
        shapes = ((geom, 1) for geom in shaperead.geometry)

    with rasterio.open(base_layer, 'r') as rst:
        meta = rst.meta.copy()
        transform = rst.transform
        height = rst.height
        width = rst.width

    meta.update(compress='lzw', dtype=rasterio.float32, count=1)

    out_arr = np.zeros((height, width), dtype=np.float32)
    burned = features.rasterize(shapes=shapes, fill=0, out=out_arr, transform=transform, all_touched=True)

    with rasterio.open(outputlayer, 'w', **meta) as out:
        out.write(burned, 1)


def proximity_raster(rasterized_path, proximity_path):
    proximity_path = Path(proximity_path)
    proximity_path.mkdir(parents=True, exist_ok=True)

    rasterized_path = Path(rasterized_path)
    outputraster = str(proximity_path / f"{rasterized_path.stem}_dist.tif")

    raster_file = gdal.Open(str(rasterized_path))
    raster_bd = raster_file.GetRasterBand(1)

    drv = gdal.GetDriverByName('GTiff')
    proximity_ds = drv.Create(
        outputraster,
        raster_file.RasterXSize,
        raster_file.RasterYSize,
        1,
        gdal.GetDataTypeByName('Float32')
    )

    proximity_ds.SetGeoTransform(raster_file.GetGeoTransform())
    proximity_ds.SetProjection(raster_file.GetProjectionRef())

    prox_band = proximity_ds.GetRasterBand(1)
    gdal.ComputeProximity(raster_bd, prox_band, ['DISTUNITS=GEO'])

    prox_array = prox_band.ReadAsArray()
    prox_array[prox_array > 5000] = np.nan
    prox_band.WriteArray(prox_array)

    prox_band.ComputeStatistics(0)
    proximity_ds = None
    raster_file = None


def score_raster(prox_path, out_fuzzy, scale_factor, a, b, atenuation_factor):
    out_fuzzy = Path(out_fuzzy)
    out_fuzzy.mkdir(parents=True, exist_ok=True)

    prox_path = Path(prox_path)
    newname = prox_path.stem.replace('_raster_dist', '')
    outputlayer = out_fuzzy / f"{newname}_scored.tif"

    with rasterio.open(prox_path) as src:
        map2array = src.read(1).astype(np.float32)
        profile = src.profile.copy()

    # Create distinct boolean masks before mutating map2array
    mask_le_a = map2array <= a
    mask_mid = (map2array > a) & (map2array <= b)
    mask_gt_b = map2array > b

    scored_array = np.empty_like(map2array, dtype=np.float32)
    scored_array[mask_le_a] = scale_factor
    scored_array[mask_mid] = np.round(
        scale_factor * (1.0 / (np.power(2.0, (map2array[mask_mid] / atenuation_factor)))), 3
    )
    scored_array[mask_gt_b] = np.nan

    profile.update(dtype=rasterio.float32)

    with rasterio.open(outputlayer, 'w', **profile) as dst:
        dst.write(scored_array, 1)


def score_raste_water(prox_path, out_fuzzy, scale_factor, a, b, atenuation_factor):
    out_fuzzy = Path(out_fuzzy)
    out_fuzzy.mkdir(parents=True, exist_ok=True)

    prox_path = Path(prox_path)
    newname = prox_path.stem.replace('_raster_dist', '')
    outputlayer = out_fuzzy / f"{newname}_scored.tif"

    with rasterio.open(prox_path) as src:
        map2array = src.read(1).astype(np.float32)
        profile = src.profile.copy()

    mask_le_a = map2array <= a
    mask_mid = (map2array > a) & (map2array <= b)
    mask_gt_b = map2array > b

    scored_array = np.empty_like(map2array, dtype=np.float32)
    scored_array[mask_le_a] = np.nan
    scored_array[mask_mid] = np.round(
        scale_factor * (1.0 / (np.power(2.0, (map2array[mask_mid] / atenuation_factor)))), 3
    )
    scored_array[mask_gt_b] = np.nan

    profile.update(dtype=rasterio.float32)

    with rasterio.open(outputlayer, 'w', **profile) as dst:
        dst.write(scored_array, 1)


def normalize(column, new_min, new_max):
    upper = np.nanmax(column)
    lower = np.nanmin(column)
    if upper == lower:
        return np.full_like(column, new_min)
    y = (column - lower) / (upper - lower) * (new_max - new_min) + new_min
    return y


def reduction(rasters_path, outcome_path):
    outcome_path = Path(outcome_path)
    outcome_path.mkdir(parents=True, exist_ok=True)

    rasters_path = Path(rasters_path)
    outputraster = str(outcome_path / f"{rasters_path.stem}.tif")

    raster_file = gdal.Open(str(rasters_path))
    creation_options = ["COMPRESS=LZW", "TILED=YES", "PREDICTOR=3", "DISCARD_LSB=10"]
    reduced_raster = gdal.Translate(outputraster, raster_file, creationOptions=creation_options)
    reduced_raster = None
    raster_file = None


def delete_files_in_directory(directory_path):
    directory_path = Path(directory_path)
    if not directory_path.exists():
        return

    for item in directory_path.iterdir():
        if item.is_file():
            try:
                item.unlink()
            except Exception as e:
                print(f"Error removing {item}: {e}")