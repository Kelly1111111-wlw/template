"""
NOAA stations data->reproject to UTM Zone 17N->create 2km buffer->reproject NCLD raster to UTM Zone 17N
->calculate mean imperviousness->calculate impervious change->save results
.\.venv\Scripts\python.exe ".\4.process_NLCD.py"
"""
from pathlib import Path
import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from rasterio.mask import mask
from rasterio.warp import calculate_default_transform, reproject, Resampling

ROOT = Path("D:/Spatial Data Science/FinalProject/data")
OUT = ROOT/"processed"
NLCD = ROOT/"raw"/"nlcd"
OUT.mkdir(parents=True, exist_ok=True)

# read selected stations data
stations = pd.read_csv(OUT/"selected_stations.csv", dtype={"station_id": str})
# convert stations to GeoDataFrame
gdf = gpd.GeoDataFrame(
    stations,
    geometry=gpd.points_from_xy(
        stations["longitude"],
        stations["latitude"]
    ),
    crs="EPSG:4326"
)
# convert to UTM Zone 17N
gdf = gdf.to_crs("EPSG:32617")
# create 2 km buffers
buffers = gdf.copy()
buffers["geometry"] = buffers.geometry.buffer(2000)
buffers.to_file(OUT/"station_2km_buffers.gpkg", driver="GPKG")

# reproject NLCD rasters(UTM Zone 17N)
def prepare_raster(year):
    src_path = NLCD/f"impervious_{year}.tiff"
    dst_path = OUT/f"impervious_{year}_utm.tif"
    with rasterio.open(src_path) as src:
        transform, width, height = calculate_default_transform(
            src.crs,
            "EPSG:32617",
            src.width,
            src.height,
            *src.bounds
        )
        profile = src.profile.copy()
        profile.update(
            driver="GTiff",
            crs="EPSG:32617",
            transform=transform,
            width=width,
            height=height,
            count=1,
            dtype="float32",
            compress="lzw",
            nodata=-9999
        )
        with rasterio.open(dst_path, "w", **profile) as dst:
            reproject(
                source=rasterio.band(src, 1),
                destination=rasterio.band(dst, 1),
                src_transform=src.transform,
                src_crs=src.crs,
                src_nodata=src.nodata,
                dst_transform=transform,
                dst_crs="EPSG:32617",
                dst_nodata=-9999,
                resampling=Resampling.nearest
            )
    print(f"Finished reprojecting {year}")
    return dst_path

paths = {}
for year in [2001, 2025]:
    paths[year] = prepare_raster(year)

# calculate mean impervious surface within each buffer
def buffer_mean(src, geometry):
    data, _ = mask(
        src,
        [geometry.__geo_interface__],
        crop=True,
        filled=False,
        all_touched=False
    )
    values = data[0].compressed()
    # valid fractional impervious values (0-100)
    values = values[(values >= 0) & (values <= 100)]
    if len(values) == 0:
        return np.nan
    return float(np.mean(values))

# calculate impervious surface for each station
results = buffers[["station_id", "station_name", "county"]].copy()
for year in [2001, 2025]:
    means = []
    with rasterio.open(paths[year]) as src:
        for geom in buffers.geometry:
            mean_value = buffer_mean(src, geom)
            means.append(mean_value)
    results[f"impervious_{year}"] = means

# calculate impervious surface change
results["impervious_change"] = (results["impervious_2025"] - results["impervious_2001"])

# save results
results.to_csv(OUT/"station_impervious_change.csv", index=False)
print(results.head())
print("Final stations:", len(results))
