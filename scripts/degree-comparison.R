# Script to compute degree comparison
# R version 4.3.0

# Load libraries
library(groundhog) # Version 3.1.0
pkgs <- c("readr")
groundhog.library(pkgs, "2023-05-01")

# setwd("")

degree <- read_delim("degree.tsv", delim = "\t", 
                   escape_double = FALSE, trim_ws = TRUE)


#Means, Standard derivations, Medians
mean(degree$Body)
sd(degree$Body)
median(degree$Body)

mean(degree$Emotion)
sd(degree$Emotion)
median(degree$Emotion)

mean(degree$Color)
sd(degree$Color)
median(degree$Color)


#T-tests
t.test(degree$Body,degree$Emotion)

t.test(degree$Body,degree$Color)

t.test(degree$Emotion,degree$Color)


