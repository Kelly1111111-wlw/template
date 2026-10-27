# January shows a very weak positive relationship, while April shows
# almost no relationship. July and October show negative relationships,
# especially July. Most stations experienced warming, but stations with
# greater impervious surface increases did not necessarily have stronger
# warming trends.
library(tidyverse)

# paths
ROOT <- "D:/Spatial Data Science/FinalProject"
DATA <- file.path(ROOT, "data/processed")
FIG <- file.path(ROOT, "figures")
dir.create(FIG, showWarnings = FALSE)

# read data
df <- read_csv(file.path(DATA, "temperature_impervious_merged.csv"))
# select TAVG
urban_temp <- df %>%
  filter(variable == "TAVG") %>%
  mutate(
    month_name = factor(
      month,
      levels = c(1, 4, 7, 10),
      labels = c("January", "April", "July", "October")
    )
  )

# plot scatterplots and regression lines
p4 <- ggplot(urban_temp, aes(x = impervious_change, y = slope_c_per_decade)) +
  geom_point(color = "#2C7FB8", size = 3, alpha = 0.8) +
  geom_smooth(method = "lm", formula = y ~ x, se = TRUE, color = "#D95F02", fill = "#FDD0A2") +
  geom_hline(yintercept = 0, linetype = "dashed", color = "gray50") +
  facet_wrap(~month_name, ncol = 2) +
  labs(
    title = "Urbanization and Temperature Trends",
    subtitle = "Impervious surface change vs. TAVG trend(2001-2025)",
    x = "Impervious Surface Change(percentage points)",
    y = "TAVG Trend(°C/decade)"
  )
print(p4)

# save PNG
ggsave(file.path(FIG, "Figure4_Regression_Urban_Temperature.png"), p4, dpi = 300)

# calculate correlation and regression statistics
regression_results <- urban_temp %>%
  group_by(month_name) %>%
  # same process to different groups
  group_modify(~ {
    model <- lm(slope_c_per_decade ~ impervious_change, data = .x)
    model_summary <- summary(model)
    correlation_test <- cor.test(
      .x$impervious_change,
      .x$slope_c_per_decade,
      method = "pearson"
    )
    # extract statistics results
    tibble(
      n = nrow(.x),
      correlation = unname(correlation_test$estimate),
      correlation_p = correlation_test$p.value,
      regression_slope = unname(coef(model)[2]),
      regression_intercept = unname(coef(model)[1]),
      r_squared = model_summary$r.squared,
      regression_p = coef(model_summary)[2, 4]
    )
  }) %>%
  ungroup()
print(regression_results)

# save statistics
write_csv(regression_results, file.path(DATA, "urbanization_regression_results.csv"))
