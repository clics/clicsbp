# Script to compute ARI statistics and create density plot
# R version 4.3.0

# Load libraries
library(groundhog) # Version 3.1.0
pkgs <- c("reshape2","ggplot2", "gridExtra", "readr", "dplyr")
groundhog.library(pkgs, "2023-05-01")

# setwd("")

body <- read_csv("./clics/clicsbp/output/ari-human_body_part.tsv")

names(body)[names(body) == "ARI"] <- "ARI_BODY"
names(body)[names(body) == "AMI"] <- "AMI_BODY"
names(body)[names(body) == "BCUBES"] <- "BCUBES_BODY"

emotion <- read_csv("./clics/clicsbp/output/ari-emotion.tsv")

names(emotion)[names(emotion) == "ARI"] <- "ARI_EMOTION"
names(emotion)[names(emotion) == "AMI"] <- "AMI_EMOTION"
names(emotion)[names(emotion) == "BCUBES"] <- "BCUBES_EMOTION"

color <- read_csv("./clics/clicsbp/output/ari-color.tsv")

names(color)[names(color) == "ARI"] <- "ARI_COLOR"
names(color)[names(color) == "AMI"] <- "AMI_COLOR"
names(color)[names(color) == "BCUBES"] <- "BCUBES_COLOR"

df1 <- full_join(body, emotion, by = c("FAMILY_A", "FAMILY_B"))
df2 <- full_join(df1, color, by = c("FAMILY_A", "FAMILY_B"))


#Means
mean(df2$ARI_BODY,na.rm=T)
sd(df2$ARI_BODY,na.rm=T)
mean(df2$AMI_BODY,na.rm=T)
sd(df2$AMI_BODY,na.rm=T)
mean(df2$BCUBES_BODY,na.rm=T)
sd(df2$BCUBES_BODY,na.rm=T)

mean(df2$ARI_EMOTION,na.rm=T)
sd(df2$ARI_EMOTION,na.rm=T)
mean(df2$AMI_EMOTION,na.rm=T)
sd(df2$AMI_EMOTION,na.rm=T)
mean(df2$BCUBES_EMOTION,na.rm=T)
sd(df2$BCUBES_EMOTION,na.rm=T)

mean(df2$ARI_COLOR,na.rm=T)
sd(df2$ARI_COLOR,na.rm=T)
mean(df2$AMI_COLOR,na.rm=T)
sd(df2$AMI_COLOR,na.rm=T)
mean(df2$BCUBES_COLOR,na.rm=T)
sd(df2$BCUBES_COLOR,na.rm=T)

#Medians
median(df2$ARI_BODY,na.rm=T)
median(df2$AMI_BODY,na.rm=T)
median(df2$BCUBES_BODY,na.rm=T)

median(df2$ARI_EMOTION,na.rm=T)
median(df2$AMI_EMOTION,na.rm=T)
median(df2$BCUBES_EMOTION,na.rm=T)

median(df2$ARI_COLOR,na.rm=T)
median(df2$AMI_COLOR,na.rm=T)
median(df2$BCUBES_COLOR,na.rm=T)


#T-tests
t.test(df2$ARI_BODY,df2$ARI_EMOTION)
t.test(df2$AMI_BODY,df2$AMI_EMOTION)
t.test(df2$BCUBES_BODY,df2$BCUBES_EMOTION)

t.test(df2$ARI_BODY,df2$ARI_COLOR)
t.test(df2$AMI_BODY,df2$AMI_COLOR)
t.test(df2$BCUBES_BODY,df2$BCUBES_COLOR)

t.test(df2$ARI_EMOTION,df2$ARI_COLOR)
t.test(df2$AMI_EMOTION,df2$AMI_COLOR)
t.test(df2$BCUBES_EMOTION,df2$BCUBES_COLOR)

#########################################
################Graphic#################
#########################################

#Density

ggplot(na.omit(df2)) + 
  geom_density(aes(x=ARI_BODY, fill="ARI_BODY"), color="darkgreen", alpha=0.7) + 
  geom_density(aes(x=AMI_BODY, fill="AMI_BODY"), color="mediumspringgreen", alpha=0.7) + 
  geom_density(aes(x=ARI_COLOR, fill="ARI_COLOR"), color="blue", alpha=0.7) + 
  geom_density(aes(x=AMI_COLOR, fill="AMI_COLOR"), color="#52ADD4", alpha=0.7) + 
  geom_density(aes(x=ARI_EMOTION, fill="ARI_EMOTION"), color="#FFA500", alpha=0.7) + 
  geom_density(aes(x=AMI_EMOTION, fill="AMI_EMOTION"), color="#FF8C00", alpha=0.7) + 
  scale_x_continuous(expand=c(0.02, 0), name ="ARI and AMI", limits = c(-0.2, 1.2)) +
  scale_y_continuous(name = "Density", expand=c(0.02, 0), limits = c(0, 4)) +
  scale_fill_manual(values = c("ARI_BODY"="darkgreen", "AMI_BODY"="mediumspringgreen", "ARI_COLOR"="blue", "AMI_COLOR"="#52ADD4", "ARI_EMOTION"="#FFA500", "AMI_EMOTION"="#FF8C00"),
                    labels = c("ARI_BODY"="ARI Body", "AMI_BODY"="AMI Body", "ARI_COLOR"="ARI Colour", "AMI_COLOR"="AMI Colour", "ARI_EMOTION"="ARI Emotion", "AMI_EMOTION"="AMI Emotion")) +
  theme_classic() +
  theme(legend.position="top", legend.justification="right", 
        legend.key.size = unit(0.5, "cm")) +
  guides(fill = guide_legend(title = "", ncol = 2, override.aes = list(linetype = c(0,0,0,0,0,0))))



ggsave("./clics/clicsbp/output/density-plot.png")
