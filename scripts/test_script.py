# -*- coding: utf-8 -*-
"""
Created on Wed Sep  2 16:09:28 2026

@author: marias
"""

from pathlib import Path
import os
import sys
import numpy as np
import rasterio
import geopandas as gpd

# =============================================================================
# 1. Directory Structure Verification
# =============================================================================

try:
    # Works when running as a .py script
    BASE_DIR = Path(__file__).resolve().parent.parent
except NameError:
    # Fallback when running inside Jupyter Notebook / IPython
    BASE_DIR = Path.cwd().resolve()
#BASE_DIR=Path(r'C:/Users/marias/OneDrive - UNBC/UNBC/Chapter_2/HDI_BC_mapping')

DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
SCRIPTS_DIR = BASE_DIR / "scripts"

# Add scripts directory to module import path
sys.path.append(str(SCRIPTS_DIR))

print("--- Testing Directory Structure ---")
print(f"Root Directory: {BASE_DIR}")

# Required input directories to verify existence
required_dirs = [
    DATA_DIR / "base_maps",
    DATA_DIR / "Accessibility" / "Navigable_Waterways",
    DATA_DIR / "Accessibility" / "Railways",
    DATA_DIR / "Build_up_areas",
    DATA_DIR / "Energy",
    DATA_DIR / "LandUse",
    DATA_DIR / "Linear_Features",
    DATA_DIR / "O&G",
    DATA_DIR / "Pop_density",
    DATA_DIR / "Recreation",
    DATA_DIR / "Roads",
]

missing_dirs = []
for d in required_dirs:
    if not d.exists():
        missing_dirs.append(d)
        print(f"[MISSING] Directory not found: {d}")
    else:
        print(f"[OK] Directory exists: {d.relative_to(BASE_DIR)}")

if missing_dirs:
    print(f"\nWARNING: {len(missing_dirs)} input directories missing. Please create them before running the main script.")
else:
    print("\nAll required input directories exist!")

print("\n" + "="*50 + "\n")

# =============================================================================
# 2. Test Function Imports
# =============================================================================

print("--- Testing Module Import ---")
try:
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
    print("[OK] Successfully imported functions from raster_functions.py")
except ImportError as e:
    print(f"[FAIL] Could not import raster_functions.py: {e}")
    sys.exit(1)

print("\n" + "="*50 + "\n")

# =============================================================================
# 3. Test Base Map Readability
# =============================================================================

print("--- Testing Base Map File ---")
base_layer = DATA_DIR / "base_maps" / "BC_Terrestrial_Map_Float.tif"

if not base_layer.exists():
    print(f"[FAIL] Base raster file missing at: {base_layer}")
    print("Please place 'BC_Terrestrial_Map_Float.tif' inside 'data/base_maps/' to run function execution tests.")
    sys.exit(1)

try:
    with rasterio.open(base_layer) as src:
        print(f"[OK] Base map successfully opened:")
        print(f"     - Dimensions: {src.width} x {src.height}")
        print(f"     - CRS: {src.crs}")
        print(f"     - Bounds: {src.bounds}")
except Exception as e:
    print(f"[FAIL] Error reading base map: {e}")
    sys.exit(1)

print("\n" + "="*50 + "\n")

# =============================================================================
# 4. Function Execution Unit Tests (Uses Temporary Test Data)
# =============================================================================

print("--- Checking All Input Folders for Shapefiles (.shp) ---")

found_shapefiles = []
missing_folders = []

for folder in required_dirs:
    if not folder.exists():
        print(f"[MISSING FOLDER] {folder.relative_to(BASE_DIR)}")
        missing_folders.append(folder)
        continue
    
    # Locate all shapefiles inside this subfolder
    shps = list(folder.glob("*.shp"))
    if shps:
        for shp in shps:
            print(f"[FOUND] {shp.relative_to(BASE_DIR)}")
            found_shapefiles.append(shp)
    else:
        print(f"[NO SHAPEFILES FOUND] in: {folder.relative_to(BASE_DIR)}")

print(f"\nInventory Summary: Found {len(found_shapefiles)} shapefile(s) across {len(required_dirs)} target folders.")
print("\n" + "="*50 + "\n")




print("--- Testing Execution of Raster Functions ---")





print("--- Testing Execution of Raster Functions ---")

# Setup temporary test directory inside output
TEST_OUT = OUTPUT_DIR / "_test_temp"
TEST_OUT.mkdir(parents=True, exist_ok=True)

# Find first available shapefile in data/ to test rasterization
sample_shp = None
for root, _, files in os.walk(DATA_DIR):
    for f in files:
        if f.endswith('.shp'):
            sample_shp = Path(root) / f
            break
    if sample_shp:
        break

if sample_shp:
    print(f"Found sample shapefile for testing: {sample_shp.relative_to(BASE_DIR)}")
    
    # Test 1: rasterize
    try:
        rasterize(str(base_layer), str(TEST_OUT), str(sample_shp))
        expected_raster = TEST_OUT / f"{sample_shp.stem}_raster.tif"
        if expected_raster.exists():
            print("[OK] Function 'rasterize()' executed successfully.")
        else:
            print("[FAIL] Function 'rasterize()' completed but output raster was not found.")
    except Exception as e:
        print(f"[FAIL] Function 'rasterize()' threw an error: {e}")

    # Test 2: proximity_raster
    rasterized_test_file = TEST_OUT / f"{sample_shp.stem}_raster.tif"
    prox_out_dir = TEST_OUT / "prox_test"
    
    if rasterized_test_file.exists():
        try:
            proximity_raster(str(rasterized_test_file), str(prox_out_dir))
            expected_dist = prox_out_dir / f"{rasterized_test_file.stem}_dist.tif"
            if expected_dist.exists():
                print("[OK] Function 'proximity_raster()' executed successfully.")
            else:
                print("[FAIL] Function 'proximity_raster()' completed but output file was not found.")
        except Exception as e:
            print(f"[FAIL] Function 'proximity_raster()' threw an error: {e}")

    # Test 3: score_raster
    dist_test_file = prox_out_dir / f"{rasterized_test_file.stem}_dist.tif"
    scored_out_dir = TEST_OUT / "scored_test"
    
    if dist_test_file.exists():
        try:
            score_raster(str(dist_test_file), str(scored_out_dir), scale_factor=5, a=10, b=1000, atenuation_factor=300)
            if len(list(scored_out_dir.glob("*.tif"))) > 0:
                print("[OK] Function 'score_raster()' executed successfully.")
            else:
                print("[FAIL] Function 'score_raster()' completed but output file was not found.")
        except Exception as e:
            print(f"[FAIL] Function 'score_raster()' threw an error: {e}")

    # Test 4: delete_files_in_directory
    try:
        delete_files_in_directory(str(prox_out_dir))
        remaining_files = list(prox_out_dir.glob("*"))
        if len(remaining_files) == 0:
            print("[OK] Function 'delete_files_in_directory()' executed successfully.")
        else:
            print("[FAIL] Function 'delete_files_in_directory()' failed to clear directory.")
    except Exception as e:
        print(f"[FAIL] Function 'delete_files_in_directory()' threw an error: {e}")

else:
    print("[SKIP] No shapefiles (.shp) found inside 'data/' directory to run function testing.")

# Test 5: normalize math function
try:
    arr = np.array([0, 5, 10], dtype=np.float32)
    norm = normalize(arr, 0, 1)
    if np.array_equal(norm, [0.0, 0.5, 1.0]):
        print("[OK] Function 'normalize()' scalar array math verified.")
    else:
        print("[FAIL] Function 'normalize()' yielded unexpected values.")
except Exception as e:
    print(f"[FAIL] Function 'normalize()' threw an error: {e}")

# Clean up test output directory
import shutil
shutil.rmtree(TEST_OUT, ignore_errors=True)

print("\n" + "="*50)
print("Testing complete!")