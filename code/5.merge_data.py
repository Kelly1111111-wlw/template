"""
read processed data->merge data->save output
.\.venv\Scripts\python.exe ".\5.merge_data.py"
"""
from pathlib import Path
import pandas as pd

OUT = Path("data/processed")

# read data
temp = pd.read_csv(OUT/"station_temperature_trends.csv", dtype={"station_id": str})
impervious = pd.read_csv(OUT/"station_impervious_change.csv", dtype={"station_id": str})

# merge by station ID
final = temp.merge(
    impervious[["station_id", "impervious_2001", "impervious_2025", "impervious_change"]],
    on="station_id",
    how="inner",
    validate="many_to_one"
)

# save output
final.to_csv(OUT/"temperature_impervious_merged.csv", index=False)
print("Records:", len(final))
print("Stations:", final["station_id"].nunique())