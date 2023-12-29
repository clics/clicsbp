# Script to compute degree comparison
# R version 4.3.0

# Load libraries
library(groundhog) # Version 3.1.0
pkgs <- c("readr", "ggplot2")
groundhog.library(pkgs, "2023-05-01")

# setwd("")

degree <- read_delim("./clics/clicsbp/output/degree-language.tsv", 
                     delim = "\t", escape_double = FALSE, 
                     trim_ws = TRUE)


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


# Density

ggplot(na.omit(degree)) + 
  geom_density(aes(x=Body, fill="Body"), color="darkgreen", alpha=0.7) + 
  geom_density(aes(x=Color, fill="Color"), color="blue", alpha=0.7) + 
  geom_density(aes(x=Emotion, fill="Emotion"), color="#FFA500", alpha=0.7) + 
  scale_x_continuous(expand=c(0.02, 0), name ="Degree", limits = c(0.0, 18)) +
  scale_y_continuous(name = "Density", expand=c(0.02, 0), limits = c(0, 0.5)) +
  scale_fill_manual(values = c("Body"="darkgreen", "Color"="blue", "Emotion"="#FFA500"), labels = c("Body"="Body", "Color"="Colour", "Emotion"="Emotion")) +
  theme_classic() +
  theme(legend.position="top", legend.justification="right", 
        legend.key.size = unit(0.5, "cm")) +
  guides(fill = guide_legend(title = "", ncol = 1, override.aes = list(linetype = c(0,0,0))))

ggsave("./clics/clicsbp/output/density-degree.png")


