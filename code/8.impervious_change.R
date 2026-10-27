# This graph used a grouped bar chart to compare impervious surface 
# percentages in 2001 and 2025 for each weather station, with horizontal
# bars and different colors for each year.
library(tidyverse)

# paths
ROOT <- "D:/Spatial Data Science/FinalProject"
DATA <- file.path(ROOT, "data/processed")
FIG <- file.path(ROOT, "figures")
dir.create(FIG, showWarnings = FALSE)

# read data
df <- read_csv(file.path(DATA, "temperature_impervious_merged.csv"))
# each station only "one" records
imp <- df %>% distinct(station_id, station_name, impervious_2001, impervious_2025, impervious_change)
# convert the columns
imp_modify <- imp %>%
  pivot_longer(cols = c(impervious_2001, impervious_2025), names_to = "year", values_to = "impervious") %>%
  mutate(year = recode(year, impervious_2001 = "2001", impervious_2025 = "2025")
  )

# plot impervious change
p3 <- ggplot(imp_modify, aes(x = reorder(station_name, impervious), y = impervious, fill = year)) +
  geom_col(position = "dodge", width = 0.7) +
  coord_flip() +
  scale_fill_manual(values = c("2001" = "#91BFDB", "2025" = "#FC8D59")) +
  labs(
    title = "Impervious Surface Change(2001-2025)",
    subtitle = "Mean imperviousness within 2 km of each station",
    x = "Weather Station",
    y = "Impervious Surface(%)",
    fill = "Year"
  )
print(p3)

# save PNG
ggsave(file.path(FIG, "Figure3_Impervious_Change.png"), p3, dpi = 300)
