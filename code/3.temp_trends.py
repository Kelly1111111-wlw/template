"""
monthly temp data->select representative months->group by station and month
->apply 20-year threshold->linear regression->export results
.\.venv\Scripts\python.exe ".\3.temp_trends.py"
"""
from pathlib import Path
import pandas as pd
from scipy.stats import linregress

OUT = Path("data/processed")
df = pd.read_csv(OUT/"monthly_temperature_2001_2025.csv")
represent_month = {
    1: "Winter",
    4: "Spring",
    7: "Summer",
    10: "Fall"
}
df = df[df["month"].isin(represent_month)].copy()
df["season"] = df["month"].map(represent_month)
df.to_csv(OUT/"season_temperature.csv", index=False)

results = []
for (sid, month), group in df.groupby(["station_id", "month"]):
    # at least 20 years
    if group["year"].nunique() < 20:
        continue

    metadata = group.iloc[0]
    for variable in ["TAVG", "TMAX", "TMIN"]:
        valid = group[["year", variable]].dropna()
        if len(valid) < 20:
            continue
        # temperature--year
        regression = linregress(valid["year"], valid[variable])
        results.append({
            "station_id": sid,
            "station_name": metadata["station_name"],
            "county": metadata["county"],
            "latitude": metadata["latitude"],
            "longitude": metadata["longitude"],
            "month": month,
            "season": represent_month[month],
            "variable": variable,
            "n_years": len(valid),
            "slope_c_per_year": regression.slope,
            "slope_c_per_decade": regression.slope * 10,
            "p_value": regression.pvalue,
            "r_squared": regression.rvalue ** 2
        })

trends = pd.DataFrame(results)

trends.to_csv(OUT/"station_temperature_trends.csv", index=False)
print(trends.head())
print("Trend records:", len(trends))