# Bayesian sample size determination

# Load the evidence package
require(evidence)

# We will peruse a worst case scenario: we have a flat prior on the binomial parameter, and the true parameter value is 0.5
# We define wrapper functions that take Nmin and Nmax (the inimum and maximum sample size considered)
estimate_95HDPI<-function(N) {
  betabinomial<-quantile(
    rbeta(500000, 
          1 + floor(N/2),
          1 + ceiling(N/2)),
    c(0.025,0.975))
  return(betabinomial[[2]]-betabinomial[[1]])}

estimate_sample_colexification<-function(Nmin,Nmax) {
  mean_95HDPI<-sapply(c(Nmin:Nmax),
                      function(x) estimate_95HDPI(x))
                      
  return(data.frame(N=c(Nmin:Nmax),D=mean_95HDPI))}

# Run analysis
sample_colexification<-estimate_sample_colexification(10,200)  

# Plot results
ggplot(sample_colexification,aes(x=N,y=D))+
  geom_line(color="darkblue",size=3)+
  theme_bw()+
  labs(x="Number of families with at least one language displaying both lexical items",
       y="95% HPDI of binomial parameter when p=0.5")+
  scale_x_continuous(limits = c(10,200),breaks = 10*c(1:20),expand = c(0,0))+
  scale_y_continuous(expand = c(0,0))+
  geom_vline(xintercept=40,color="red")+
  geom_vline(xintercept=90,color="red")

ggsave("sample_bayesian_colexification.png",height=5)
