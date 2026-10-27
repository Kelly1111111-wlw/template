# In January and April, most stations are above the dashed line, indicating
# that minimum temperatures increased faster than maximum temperatures. 
# July shows mixed results, while October shows the opposite pattern, with
# TMAX increasing faster than TMIN at most stations.
library(tidyverse)

# paths
ROOT <- "D:/Spatial Data Science/FinalProject"
DATA <- file.path(ROOT, "data/processed")
FIG <- file.path(ROOT, "figures")
dir.create(FIG, showWarnings = FALSE)

# read data
df <- read_csv(file.path(DATA, "temperature_impervious_merged.csv"))

# select TMIN and TMAX
temp_compare <- df %>%
  filter(variable %in% c("TMIN", "TMAX")) %>%
  select(station_id, station_name, month, variable, slope_c_per_decade) %>%
  pivot_wider(names_from = variable, values_from = slope_c_per_decade) %>%
  mutate(
    month_name = factor(
      month,
      levels = c(1, 4, 7, 10),
      labels = c("January", "April", "July", "October")
    )
  )
# calculate TMIN - TMAX trend difference
temp_compare <- temp_compare %>%
  mutate(trend_difference = TMIN - TMAX)

# plot TMIN vs. TMAX trends
p5 <- ggplot(temp_compare, aes(x = TMAX, y = TMIN)) +
  # reference line: TMIN = TMAX
  geom_abline(slope = 1, intercept = 0, linetype = "dashed", color = "gray50", linewidth = 0.7) +
  # weather stations
  geom_point(aes(color = trend_difference), size = 3.5, alpha = 0.9) +
  # 4 representative months
  facet_wrap(~month_name, ncol = 2) +
  # Color represents TMIN - TMAX(trend)
  scale_color_gradient2(
    low = "#4575B4",
    mid = "white",
    high = "#D73027",
    midpoint = 0,
    name = "TMIN - TMAX\n(°C/decade)"
  ) +
  labs(
    title = "Comparison of TMIN and TMAX Temperature Trends",
    subtitle = "Nine weather stations in Western New York(2001-2025)",
    x = "TMAX Trend(°C/decade)",
    y = "TMIN Trend(°C/decade)",
    caption = "Dashed line represents equal TMIN and TMAX trends."
  ) 
print(p5)

# save PNG
ggsave(filename = file.path(FIG, "Figure5_TMIN_vs_TMAX_Trends.png"), plot = p5, dpi = 300)

# summary statistics
difference_summary <- temp_compare %>%
  group_by(month_name) %>%
  summarise(
    n = n(),
    mean_TMIN = mean(TMIN),
    mean_TMAX = mean(TMAX),
    mean_difference = mean(trend_difference),
    median_difference = median(trend_difference),
    stations_TMIN_faster = sum(trend_difference > 0),
    .groups = "drop"
  )
print(difference_summary)

# save summary statistics
write_csv(difference_summary, file.path(DATA, "tmin_tmax_comparison.csv"))
# save station-level differences
write_csv(temp_compare, file.path(DATA, "station_tmin_tmax_differences.csv"))

