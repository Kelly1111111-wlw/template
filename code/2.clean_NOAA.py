"""
NOAA data->clean daily observations->calculate monthly temp->apply 80% daily completeness(month)
->apply 95% monthly completeness(station)->merge & export data
.\.venv\Scripts\python.exe ".\2.clean_NOAA.py"
"""
from pathlib import Path
import calendar
import pandas as pd
import calendar

START_YEAR = 2001
END_YEAR = 2025
# read the data
RAW = Path("data/raw/noaa")
OUT = Path("data/processed")
stations = pd.read_csv(OUT/"wny_candidate_stations.csv", dtype={"station_id": str})

def read_dly(path):
    records = []
    # open the .dly records
    with open(path, "r") as f:
        for line in f:
            station_id = line[0:11]
            year = int(line[11:15])
            month = int(line[15:17])
            element = line[17:21]
            # year： 2001-2025
            if not (START_YEAR <= year <= END_YEAR):
                continue
            # only need TMAX and TMIN value
            if element not in ("TMAX", "TMIN"):
                continue
            # return how many days in this month
            ndays = calendar.monthrange(year, month)[1]

            # get the temperature value
            for day in range(1, ndays + 1):
                start = 21 + (day - 1) * 8
                value = int(line[start:start + 5])
                qflag = line[start + 6:start + 7]
                # Missing or quality-flagged observations
                if value == -9999 or qflag.strip():
                    continue
                records.append({
                    "station_id": station_id,
                    "date": pd.Timestamp(year, month, day),
                    "element": element,
                    "temperature": value / 10.0
                })
    return pd.DataFrame(records)

all_monthly = []
for sid in stations["station_id"]:
    path = RAW/f"{sid}.dly"
    if not path.exists():
        continue

    daily = read_dly(path)
    if daily.empty:
        continue

    # station, date, TMAX and TMIN as columns
    daily = daily.pivot_table(
        index=["station_id", "date"],
        columns="element",
        values="temperature",
        aggfunc="first"
    ).reset_index()

    # skip stations that do not have both TMAX and TMIN columns
    if not {"TMAX", "TMIN"}.issubset(daily.columns):
        continue
    # drop observations with missing TMAX and TMIN values
    daily = daily.dropna(subset=["TMAX", "TMIN"])
    # drop observations with inconsistent values
    daily = daily[daily["TMAX"] >= daily["TMIN"]].copy()
    # calculate average temp
    daily["TAVG"] = (daily["TMAX"] + daily["TMIN"]) / 2
    # get the year and month values
    daily["year"] = daily["date"].dt.year
    daily["month"] = daily["date"].dt.month

    # group data by station, year, and month
    grouped = daily.groupby(["station_id", "year", "month"])
    # calculate monthly statistics(mean)
    monthly = grouped["TMAX"].mean().reset_index()
    monthly["TMIN"] = grouped["TMIN"].mean().to_numpy()
    monthly["TAVG"] = (monthly["TMAX"] + monthly["TMIN"]) / 2
    monthly["valid_days"] = grouped["date"].count().to_numpy()
    #calculate monthly completeness
    days = []
    for year, month in zip(monthly["year"], monthly["month"]):
        n_days = calendar.monthrange(year, month)[1]
        days.append(n_days)
    monthly["days_in_month"] = days
    monthly["completeness"] = monthly["valid_days"] / monthly["days_in_month"]
    # Monthly threshold >= 80%
    monthly = monthly[monthly["completeness"] >= 0.80].copy()

    all_monthly.append(monthly)

if not all_monthly:
    raise RuntimeError("No valid NOAA monthly records.")

monthly_all = pd.concat(all_monthly, ignore_index=True)
# expected 25 years * 12 months = 300
completeness = monthly_all.groupby("station_id").size().reset_index(name="valid_months")
# calculate each stations' monthly completness
completeness["monthly_completeness"] = (completeness["valid_months"] / 300)
# at least 285 valid month records
valid_stations = completeness[completeness["monthly_completeness"] >= 0.95]["station_id"]
# keep the final valid stations' temp records
monthly_final = monthly_all[monthly_all["station_id"].isin(valid_stations)].copy()
# keep the final valid stations
stations_final = stations[stations["station_id"].isin(valid_stations)].copy()

# merge county and station information(left join)
monthly_final = monthly_final.merge(
    stations_final[["station_id", "station_name", "county",
                    "latitude", "longitude"]],
    on="station_id",
    how="left"
)

# write the cleaned data
monthly_final.to_csv(OUT/"monthly_temperature_2001_2025.csv", index=False)
stations_final.to_csv(OUT/"selected_stations.csv", index=False)
completeness.to_csv(OUT/"station_completeness.csv", index=False)
print("Final stations:", len(stations_final))
print("Monthly records:", len(monthly_final))