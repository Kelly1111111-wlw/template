# Code Description

This folder contains Python and R scripts for the project.

The Python scripts are used for data downloading, cleaning, and processing. The R scripts are used for data analysis and visualization.

## Python Scripts

1. '1.down_NOAA.py'

Downloads county boundaries and NOAA weather station data. Selects stations within five counties in Western New York.

Output: 'wny_counties.gpkg', 'wny_candidate_stations.csv', and NOAA '.dly' files.

2. '2.clean_NOAA.py'

Cleans daily temperature records and calculates monthly TAVG, TMAX, and TMIN. Keeps months with at least 80% valid daily data and stations with at least 95% valid months.

Output: 'monthly_temperature_2001_2025.csv', 'selected_stations.csv', and 'station_completeness.csv'.

3. '3.temp_trends.py'

Selects January, April, July, and October as representative months for Spring, Summer, Autumn and Winter. Uses linear regression to calculate temperature trends for stations with at least 20 years of data.

Output: 'season_temperature.csv' and 'station_temperature_trends.csv'.

4. '4.process_NLCD.py'

Creates 2 km buffers around weather stations. Calculates mean impervious surface percentages for 2001 and 2025 and their changes.

Output: 'station_impervious_change.csv', station buffers, and reprojected raster files.

5. '5.merge_data.py'

Combines temperature trends and impervious surface changes using station IDs.

Output: 'temperature_impervious_merged.csv'.

## R Scripts

6. '6.TAVG_trends.R'

Compares average temperature trends across four representative months.

Output: Figure 1 – Temperature Trends.

7. '7.spatical_temp_trends.R'

Maps weather station temperature trends and impervious surface changes in Western New York.

Output: Figure 2 – Temperature and Urbanization Map.

8. '8.impervious_change.R'

Compares impervious surface percentages in 2001 and 2025 for each weather station.

Output: Figure 3 – Impervious Surface Change.

9. '9.regress_urban_temp_trends.R'

Uses linear regression to examine the relationship between impervious surface changes and TAVG trends.

Output: Figure 4 – Urbanization and Temperature Regression, and 'urbanization_regression_results.csv'.

10. '10.Tmax_Tmin_trends.R'

Compares TMIN and TMAX temperature trends for each representative month.

Output: Figure 5 – TMIN vs. TMAX Trends, and comparison CSV files.

## Data and Figures

Input and processed data are stored in the 'data/' folder.

All generated figures are saved in the 'figures/' folder.