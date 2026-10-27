"""
Download Boundaries data->Download stations data->Select stations->Download selected stations data
.\.venv\Scripts\python.exe ".\1.down_NOAA.py"
"""
from pathlib import Path
import pandas as pd
import geopandas as gpd
import requests

# set the download NOAA data roots
ROOT = Path("D:/Spatial Data Science/FinalProject/data")
RAW = ROOT/"raw/noaa"
BOUNDARY = ROOT/"raw/boundaries"
PROCESSED = ROOT/"processed"

for p in [RAW, BOUNDARY, PROCESSED]:
    p.mkdir(parents=True, exist_ok=True)

BASE = "https://www.ncei.noaa.gov/pub/data/ghcn/daily"
COUNTIES = {
    "36003": "Allegany",
    "36009": "Cattaraugus",
    "36013": "Chautauqua",
    "36029": "Erie",
    "36063": "Niagara"
}

# 1.Download county boundaries(Western New York)
county_url = (
    "https://www2.census.gov/geo/tiger/"
    "TIGER2024/COUNTY/tl_2024_us_county.zip"
)
counties = gpd.read_file(county_url)
counties = counties[counties["GEOID"].isin(COUNTIES.keys())].copy()
counties = counties.to_crs("EPSG:4326")
counties.to_file(BOUNDARY/"wny_counties.gpkg", driver="GPKG")
print("Counties:", counties["NAME"].tolist())

# 2.Download station metadata(Global Historical Climatology Network–Daily)
station_file = RAW/"ghcnd-stations.txt"
if not station_file.exists():
    r = requests.get(f"{BASE}/ghcnd-stations.txt", timeout=120)
    r.raise_for_status()
    station_file.write_bytes(r.content)
# NOAA fixed-width format:
# (0,11)->station_id; (12,20)->latitude; (21,30)->longitude; (31,37)->elevation; (38,40)->state; (41,47)->station_name
stations = pd.read_fwf(
    station_file,
    colspecs=[(0, 11), (12, 20), (21, 30), (31, 37), (38, 40), (41, 71)],
    names=["station_id", "latitude", "longitude", "elevation", "state", "station_name"],
    dtype={"station_id": str}
)
stations = stations[stations["state"] == "NY"].copy()
# change into "GeoDataFrame"
station_gdf = gpd.GeoDataFrame(
    stations,
    geometry=gpd.points_from_xy(
        stations.longitude,
        stations.latitude
    ),
    crs="EPSG:4326"
)

# 3.Select stations(5 counties)
selected = gpd.sjoin(
    station_gdf,
    counties[["GEOID", "NAME", "geometry"]],
    how="inner",
    predicate="within"
)
# delete not useful columns
selected = selected.drop(columns=["index_right"])
selected = selected.rename(columns={"NAME": "county"})
selected.to_csv(PROCESSED/"wny_candidate_stations.csv", index=False)
print("Candidate stations:", len(selected))

# 4.Download station .dly files
def download_station(station_id):
    path = RAW/f"{station_id}.dly"
    if path.exists() and path.stat().st_size > 0:
        return station_id, True
    try:
        r = requests.get(f"{BASE}/all/{station_id}.dly", timeout=90)
        r.raise_for_status()
        path.write_bytes(r.content)
        return station_id, True
    except requests.RequestException:
        return station_id, False
    
ids = selected["station_id"].unique()
failed = []
for sid in ids:
    station_id, success = download_station(sid)
    if not success:
        failed.append(station_id)
print("Failed downloads:", failed)