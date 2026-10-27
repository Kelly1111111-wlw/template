# Data Description

This folder contains the data used for the project. The study focuses on five counties in Western New York: Erie, Niagara, Chautauqua, Cattaraugus, and Allegany.

## 1. Raw Data (`raw/`)

The raw data come from three main sources:

- noaa/: Daily weather station records from NOAA GHCN-Daily, used to calculate minimum (TMIN), maximum (TMAX), and average (TAVG) temperatures.
- nlcd/: Impervious surface data for 2001 and 2025 from the National Land Cover Database (NLCD), used to measure urbanization changes.
- boundaries/: County boundaries for the five study counties, used for spatial analysis and mapping.

## 2. Processed Data (`processed/`)

This folder contains cleaned data and analysis results generated using Python and R.

- Temperature data: Monthly temperature records, selected weather stations, data completeness, and seasonal temperature trends.
- Urbanization data: Reprojected impervious surface rasters, 2 km station buffers, and impervious surface changes.
- Combined data: Temperature trends merged with impervious surface changes for each station.
- Statistical results: Regression results and comparisons between TMIN and TMAX temperature trends.

## 3. Data Processing

The NOAA records were cleaned and converted into monthly temperature averages for 2001–2025. Stations were selected based on data completeness. Temperature trends were calculated for January, April, July, and October.

Impervious surface values were calculated within 2 km buffers around each weather station. Finally, the temperature and urbanization data were combined to examine their relationships.

The Python and R scripts used for processing and analysis are available in the `code/` folder.