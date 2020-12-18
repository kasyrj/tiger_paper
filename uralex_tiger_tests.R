# Set working directory to R file location before running.

packages <- c("ggpubr",
              "dplyr",
              "rstatix",
              "car",
              "moments"
              )

package.check <- lapply(
  packages,
  FUN = function(x) {
    if (!require(x, character.only = TRUE)) {
      install.packages(x, dependencies = TRUE)
      library(x, character.only = TRUE)
    }
  }
)

# Read data
uralex.rates <-read.csv("analyses/uralex/uralex_rates.txt", sep="\t", header=FALSE)
uralex.suppl <- read.csv("uralex_supplement.tsv", sep="\t")
uralex.data <- merge(uralex.rates, uralex.suppl, by.x = "V1", by.y = "Meaning")
uralex.data$Category <- factor(uralex.data$Category)
uralex.data$Basic_vocabulary <- factor(uralex.data$Basic_vocabulary)
uralex.data <- uralex.data %>%
  rename(
    meaning = V1,
    tiger.rate = V2
  )

# Outlier identification
uralex.data %>%
  identify_outliers(tiger.rate)

## Differences between word classes

# make filtered version without adverbs (n=2) and items with 1.0 TIGER value. Recheck outliers
uralex.pruned <- uralex.data %>%
  filter(Category != "Adverb" 
         ,tiger.rate != 1.0
  )

uralex.pruned %>%
  identify_outliers(tiger.rate)

# Density plots of TIGER values (raw unfiltered data)
p <- ggdensity(uralex.data, x="tiger.rate",
               color="Category", fill="Category",
               main="Word class TIGER value distributions (raw unfiltered data)")
ggpar(p, legend.title = "Word class")

p <- ggdensity(uralex.data, x="tiger.rate",
               main="TIGER value distribution (raw unfiltered data)",
               xlab="")
ggpar(p)

# Density plots of TIGER values (raw filtered data)
p <- ggdensity(uralex.pruned, x="tiger.rate",
               color="Category", fill="Category",
               main="Word class TIGER value distributions (raw filtered data)",
               xlab="")
ggpar(p, legend.title = "Word class")

p <- ggdensity(uralex.pruned, x="tiger.rate",
               main="TIGER value distribution (raw filtered data)",
               xlab="")
ggpar(p)

# lm of raw filtered data
model.raw <- lm(tiger.rate ~ Category, data = uralex.pruned)

# Shapiro-Wilk and D'Agostino normality tests (p < 0.05: non-normal)
shapiro.test(model.raw$residuals)
agostino.test(model.raw$residuals)

# set up log-transformed versions of filtered data
uralex.pruned$log.tiger.rate <- log(uralex.pruned$tiger.rate)

# Density plots of TIGER values (log-transformed filtered data)
p <- ggdensity(uralex.pruned, x="log.tiger.rate",
               color="Category", fill="Category",
               main="Word class TIGER value distributions (log-transformed filtered data)",
               xlab="")
ggpar(p, legend.title = "Word class")

p <- ggdensity(uralex.pruned, x="log.tiger.rate",
               main="TIGER value distribution (log-transformed filtered data)",
               xlab="")
ggpar(p)

# lm of log-transformed filtered data
model.log <- lm(log.tiger.rate ~ Category, data = uralex.pruned)

# Shapiro-Wilk and D'Agostino normality tests of log-transformed data (p < 0.05: non-normal)
shapiro.test(model.log$residuals)
agostino.test(model.log$residuals)

# Homogeneity of variances of log-transformed data (p < 0.05: unequal variances)
bartlett.test(log.tiger.rate ~ Category, data = uralex.pruned)
levene_test(log.tiger.rate ~ Category, data = uralex.pruned)

# Classic ANOVA and Welch ANOVA (log-transformed data) (p < 0.05: differences between classes)
anova(model.log)
oneway.test(tiger.rate ~ Category, data = uralex.pruned, var.equal = FALSE)     # Welch ANOVA

# Tukey HSD (log-transformed data)
tukey_hsd(model.log)

# means of categories closest to being significant
mean(uralex.pruned[uralex.pruned$Category == "Noun",]$tiger.rate)
mean(uralex.pruned[uralex.pruned$Category == "Adjective",]$tiger.rate)
mean(uralex.pruned[uralex.pruned$Category == "Verb",]$tiger.rate)

## Differences between basic vs. nonbasic vocabulary

# set up filtered & log-transformed model without removing adverbs
uralex.pruned2 <- uralex.data %>%
  filter(tiger.rate != 1.0
  )

uralex.pruned2 %>%
  identify_outliers(tiger.rate)

uralex.pruned2$log.tiger.rate <- log(uralex.pruned2$tiger.rate)
model2.log <- lm(log.tiger.rate ~ Basic_vocabulary, data = uralex.pruned2)

# Shapiro-Wilk and D'Agostino normality tests (p < 0.05: non-normal)
shapiro.test(model2.log$residuals)
agostino.test(model2.log$residuals)

# Homogeneity of variances of log-transformed data (p < 0.05: unequal variances)
bartlett.test(log.tiger.rate ~ Category, data = uralex.pruned2)
levene_test(log.tiger.rate ~ Category, data = uralex.pruned2)

# Welch ANOVA and classic ANOVA (log-transformed filtered data) (p < 0.05: differences between classes)
anova(model2.log)
oneway.test(log.tiger.rate ~ Basic_vocabulary, data = uralex.pruned2, var.equal = FALSE) # Welch ANOVA

# means of basic and non-basic vocabulary
mean(uralex.pruned2[uralex.pruned2$Basic_vocabulary == "yes",]$tiger.rate)
mean(uralex.pruned2[uralex.pruned2$Basic_vocabulary == "no",]$tiger.rate)
