# Human Disturbance Index / Cumulative Pressure Mapping Workflow

Python pipeline to generate cumulative human-pressure (disturbance) rasters for British Columbia. The code processes multiple spatial pressure layers (roads, waterways, railways, linear features, dams/reservoirs, land use, population density, buildings, oil & gas, recreation) and aggregates them into a Human Disturbance Index (HDI).

The workflow is designed for British Columbia but can be adapted to other regions by substituting equivalent datasets and adjusting scoring parameters.

> **Note:** This repository contains **code only**. All input datasets are publicly available from their respective providers and must be downloaded separately.

---

Requirements
Python 3.9+

Core packages:

numpy

rasterio

gdal / osgeo

Custom module:

scripts/raster_functions.py (must be in the scripts/ folder relative to this repo)

Install dependencies (example):

bash
pip install numpy rasterio
# GDAL/osgeo usually installed via conda or system packages
Project structure
Expected folder layout:

text
project-root/
  main_pressure_mapping.py      # main script (this repo)
  scripts/
    raster_functions.py         # custom raster functions (this repo)
  data/                         # raw inputs (NOT in this repo)
    Roads/
    Accessibility/
      Navigable_Waterways/
      Railways/
    Linear_Features/
    Energy/
    LandUse/
      aci_2021_bc_clipped.tif
    Pop_density/
      Pop_density_2021.shp
    Build_up_areas/
      Buildings.shp
    O&G/
    Recreation/
    base_maps/
      BC_Terrestrial_Map_Float.tif
  output/                       # generated rasters (NOT in this repo)
    Roads/
    Navigable_Waterways/
    Railways/
    Linear_Features/
    Dams_and_Reservoirs/
    Human_Pressures/
    Human_Pressures2/
    BC_HDI/
      BC_HDI.tif

Data (not included)

Raw input data are not included in this repository. To run the pipeline, obtain the required datasets from the listed data sources and place them under data/, as shown above. Some input datasets were preprocessed before being used in the pipeline, including digitizing certain features (e.g., mining sites), classifying roads by type, extracting recreational features from other data sources, and other related processing steps.

Key inputs include:

Road, railway, and linear-feature shapefiles

Navigable waterways and dams/reservoirs shapefiles

Land-use raster: data/LandUse/aci_2021_bc_clipped.tif

Population density: data/Pop_density/Pop_density_2021.shp

Buildings: data/Build_up_areas/Buildings.shp

Oil & gas features: data/O&G/*.shp

Recreation features: data/Recreation/*.shp

Base map reference raster: data/base_maps/BC_Terrestrial_Map_Float.tif

If you are reusing this code, adjust paths and field names in the script to match your own data schema.

Running the pipeline
From the project root:

bash
python main_pressure_mapping.py
The script will:

Rasterize vector layers using the base map as reference.

Generate proximity rasters.

Apply exponential scoring functions (with layer-specific parameters).

Merge scored layers into per-pressure rasters under output/Human_Pressures/.

Optionally reduce file sizes into output/Human_Pressures2/.

Aggregate all pressures into a single HDI raster at output/BC_HDI/BC_HDI.tif.

Intermediate folders (e.g., output/Roads/, output/Navigable_Waterways/) are created and cleaned as needed by the script.

Outputs
Main outputs:

Individual pressure rasters: output/Human_Pressures/*.tif

Size-reduced pressures: output/Human_Pressures2/*.tif

Final HDI: output/BC_HDI/BC_HDI.tif

All output/ contents are excluded from version control via .gitignore.

Notes
The code assumes Windows-style paths but uses pathlib, so it should work on other OSes with minor adjustments.

Parameters for scoring (scale factors, direct/indirect distances, attenuation) are hard-coded per pressure type; modify them in the script as needed for your study area or methodology.

## Citation

If you use this code in your work, please cite:

> IS BRITISH COLUMBIA A 'SUPER NATURAL' PROVINCE? EVIDENCE FROM THE HUMAN DISTURBANCE INDEX

Example:

> XXXXXX

Also cite the original data sources as indicated in [DATA_REQUIREMENTS.md](DATA_REQUIREMENTS.md).

---

## Contact

For questions or issues, please open an issue on GitHub or contact:

- Miguel Arias  
- mifariaspa@gmail.com, marias@unbc.ca