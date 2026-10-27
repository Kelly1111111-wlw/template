# This map shows temperature trends and urbanization changes in Western New York from 2001 to 2025.
# Redder circles mean faster warming, and larger circles mean more urbanization.
# October shows the strongest warming, while April shows the weakest warming.
# Some stations near Buffalo have larger urbanization changes.
# Overall, warming rates and urbanization changes are different across locations and months.
library(tidyverse)
library(sf)

# paths
ROOT <- "D:/Spatial Data Science/FinalProject"
DATA <- file.path(ROOT, "data/processed")
FIG <- file.path(ROOT, "figures")

# read data
df <- read_csv(file.path(DATA, "temperature_impervious_merged.csv"))
counties <- st_read(file.path(ROOT, "data/raw/boundaries/wny_counties.gpkg"))
# reproject county boundaries to UTM Zone 17N
counties <- st_transform(counties, 32617)
# create county label locations
county_labels <- st_point_on_surface(counties)

# select TAVG trends
map_data <- df %>%
  filter(variable == "TAVG") %>%
  mutate(
    month_name = factor(
      month,
      levels = c(1, 4, 7, 10),
      labels = c("January", "April", "July", "October")
    )
  )

# convert stations to sf points
stations_sf <- st_as_sf(map_data, coords = c("longitude", "latitude"), crs = 4326)
stations_sf <- st_transform(stations_sf, 32617)

# plot temp vs. ubran
p2 <- ggplot() +
  # county boundaries
  geom_sf(data = counties, fill = "gray95", color = "gray50", linewidth = 0.5) +
  # weather stations
  geom_sf(data = stations_sf, aes(color = slope_c_per_decade, size = impervious_change), alpha = 0.85, show.legend = TRUE) +
  # county names
  geom_sf_text(data = county_labels, aes(label = NAME), size = 2.5, color = "gray20", check_overlap = TRUE) +
  # 4 representative months
  facet_wrap(~month_name, ncol = 2) +
  # temp trend color
  scale_color_gradient2(low = "#4575B4", mid = "white", high = "#D73027", midpoint = 0, name = "TAVG trend\n(°C/decade)") +
  # Impervious surface change size
  scale_size_continuous(range = c(2, 8), name = "Impervious change\n(percentage points)") +
  labs(
    title = "Temperature Trends and Urbanization Change",
    subtitle = "Western New York (2001-2025)",
    caption = paste(
      "Color: TAVG trend | Size: Impervious surface change",
      "| 2 km station buffers"
    )
  )
print(p2)

# save PNG
ggsave(filename = file.path(FIG, "Figure2_Temperature_Urbanization_Map.png"), plot = p2, dpi = 300)


