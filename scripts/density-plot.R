# R version: R-4.1.

# Load libraries
library(groundhog) # Version 1.5.0
pkgs <- c("reshape2","ggplot2", "gridExtra", "readr", "dplyr")
groundhog.library(pkgs, "2021-11-28")


# setwd("")

body <- read_delim("./clics/clicsbp/output/ari-body.tsv", 
                       delim = "\t", escape_double = FALSE, 
                       trim_ws = TRUE)
emotion <- read_delim("./clics/clicsbp/output/ari-emotion.tsv", 
                   delim = "\t", escape_double = FALSE, 
                   trim_ws = TRUE)

color <- read_delim("./clics/clicsbp/output/ari-color.tsv", 
                   delim = "\t", escape_double = FALSE, 
                   trim_ws = TRUE)

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
################Graphing#################
#########################################

#Density
ggplot(na.omit(df2)) + 
  geom_density(aes(x=ARI_BODY),color="darkgreen",fill="darkgreen",alpha=0.7) + 
  geom_density(aes(x=AMI_BODY),color="mediumspringgreen",fill="mediumspringgreen",alpha=0.7) + 
  geom_density(aes(x=ARI_COLOR),color="blue",fill="blue",alpha=0.7) + 
  geom_density(aes(x=AMI_COLOR),color="#52ADD4",fill="#52ADD4",alpha=0.7) + 
  geom_density(aes(x=ARI_EMOTION),color="#FFA500",fill="#FFA500",alpha=0.7) + 
  geom_density(aes(x=AMI_EMOTION),color="#FF8C00",fill="#FF8C00",alpha=0.7) + 
  scale_x_continuous(expand=c(0.02,0), name ="ARI and AMI", limits = c(-0.2,1.2)) +
  scale_y_continuous(expand=c(0.02,0), limits = c(0,6)) +
  theme_classic()

ggsave("graph.png")
