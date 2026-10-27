# Western New York became warmer from 2001 to 2025. 
# October had the fastest warming, followed by July and January. 
# April had the slowest warming, and a few stations showed cooling. 
# Overall, temperature trends were different across months and locations.
library(tidyverse)

# paths
ROOT <- "D:/Spatial Data Science/FinalProject"
DATA <- file.path(ROOT, "data/processed")
FIG <- file.path(ROOT, "figures")
dir.create(FIG, showWarnings = FALSE)

# read data
df <- read_csv(file.path(DATA, "temperature_impervious_merged.csv"))
tavg <- df %>%
  filter(variable == "TAVG") %>%
  mutate(season = factor(
      season,
      levels = c("Winter", "Spring", "Summer", "Fall"),
      labels = c("Jan", "Apr", "Jul", "Oct")
    )
  )

# plot temperature trends
p1 <- ggplot(tavg, aes(x = season, y = slope_c_per_decade)) +
  geom_boxplot(fill = "lightblue", alpha = 0.5, width = 0.5) +
  geom_jitter(width = 0.1, size = 2, alpha = 0.7) +
  geom_hline(yintercept = 0, linetype = "dashed", color = "gray40") +
  labs(
    title = "Temperature Trends in Western New York(2001-2025)",
    subtitle = "TAVG trends for four representative months",
    x = "Month",
    y = "Temperature trend(°C/decade)"
  )

print(p1)

# save figures
ggsave(file.path(FIG, "Figure1_TAVG_Trends.png"), plot = p1, dpi = 300)
