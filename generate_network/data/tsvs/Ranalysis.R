
ra <- read.csv(file="/Users/dolano/htdocs/dama-larca/d3/generate_network/data/tsvs/testing2.csv",header = T, sep=',')
dim(ra)       #247 x 45 
colnames(ra)
#"name"  "succeeded" "skipped" "aas_succeed" "aas_skip"  "aas_sport"  "aas_dupe"  "aas_empty" "aas_notfound"  "aas_list"

#e = read.csv(file = "/Users/dolano/htdocs/dama-larca/d3/generate_network/data/numbers/outputthusfar8.csv",header = TRUE, dec = ".", stringsAsFactors=FALSE)
#dim(e)       #246 x 7   (a person is missing)

edb = read.csv(file = "/Users/dolano/htdocs/dama-larca/d3/generate_network/entitiesoutput.csv",header = FALSE, dec = ".",stringsAsFactors=FALSE)
colnames(edb) <- c("name","level","position","party")

#in ra he's Eddie Lucio Jr
#in edb he's Eddie Lucio Jr.    fucking period!


md <- merge(ra,edb, by="name")
nrow(md)   #this is only 246  so we are good now

for(a in 1:nrow(ra)){   
  if(nrow(md[which(md$name == ra[a,1]),]) == 0){ 
    print("This dude isn't in the mergedData:");
    print(ra[a,1]);  #only bob is missing :)
  }
}


md$level = factor(md$level, levels=c("statewide-active", "federal-active" ,"statewide-active-elected"))
md$position = factor(md$position)
md$party = factor(md$party)

summary(md)    #46 - level,   47 - position,  48 - party

#now merge in District stuff from configdesc.json
library(rjson)
configdesc <- "/Users/dolano/htdocs/dama-larca/d3/whoyouelect-april27/js/configdesc.json"
entities_meta <- fromJSON(file=configdesc, method='C')

md$info1 <- ""
md$info2 <- ""
md$image <- ""

for(e in 1:nrow(md)){
  name <- as.character(md[e,]$name)
  meta <- entities_meta[name]
  md[e,]$info1 <- meta[[1]]$info1
  md[e,]$info2 <- meta[[1]]$info2
  md[e,]$image <- meta[[1]]$image
}

colnames(md)

#SHOW TOP 20 PEOPLE WITH THE MOST TOTAL ARTICLES   name succ, level, pos, party, succ, skipp, sport, dupe, empty, notfound list,
head(md[order(md$succeeded,decreasing = TRUE),c(1,2,46,47,48,  4,11,18,25,32,39,  5,12,19,26,33,40,   6,13,20,27,34,41,    7,14,21,28,35,42,  8,15,22,29,36,43,  9,16,23,30,37,44,  10,17,24,31,38,45)],20)
library(xtable)
#toptwenty <- xtable(head(md[order(md$succeeded,decreasing = TRUE),c(1,2,46,47,48)],20))
#toptwenty <- xtable(head(md[order(md$succeeded,decreasing = TRUE),c(1,2,46,47,48,  4,11,18,25,32,39,  5,12,19,26,33,40,   6,13,20,27,34,41,    7,14,21,28,35,42,  8,15,22,29,36,43,  9,16,23,30,37,44,  10,17,24,31,38,45)],247))
toptwenty <- xtable(head(md[order(md$succeeded,decreasing = TRUE),c(51,1,46,47,48,50,2,  4,11,18,25,32,39,  5,12,19,26,33,40,   6,13,20,27,34,41,    7,14,21,28,35,42,  8,15,22,29,36,43,  9,16,23,30,37,44,  10,17,24,31,38,45)],247))
print(toptwenty, type="html")

#THESE ABOVE WERE USED TO CREATE THE MEDIA RESULTS LONG TABLE VIEW



plotDistribution <- function(succeeded){
  d = density(md[,succeeded])
  plot(d$x,d$y * sum(md[,succeeded]),type="l",xlab="num of articles",ylab="people")
  abline(v=mean(md[,succeeded]),lty=2,col=2)
  #abline(v=median(md[,succeeded]),lty=2,col=9)
  lwr = quantile(md[,succeeded],.025) #(mean(md[,11])-(1*sd(md[,11])))    #<--- do this correctly so it shows 5% cutoff 
  upr = quantile(md[,succeeded],.975) #(mean(md[,11])+(1*sd(md[,11])))    #<--- do this so it shows 95% cutoff 
  abline(v=lwr, lty=2,col=4)
  abline(v=upr, lty=2,col=4)
  #text(3100,120,labels = "Distribution of Articles\nProcessed per Person")       
  #text(3000,80,labels = "Distribution of Articles\nSkipped per Person")       
  text(5100,120,labels = "Distribution of Articles\nDownloaded per Person")       
  #text(3000,65,labels = paste("mean at: ",toString(round(mean(md[,succeeded]),2))), col=2)
  #text(3000,50,labels = paste("median at: ",toString(round(median(md[,succeeded]),2))), col=2)
  #text(3000,35,labels = paste("[",toString(round(lwr,2)),", ",toString(round(upr,2)),"]"), col=4)
  text(5000,65,labels = paste("mean at: ",toString(round(mean(md[,succeeded]),2))), col=2)
  text(5000,50,labels = paste("median at: ",toString(round(median(md[,succeeded]),2))), col=2)
  text(5000,35,labels = paste("[",toString(round(lwr,2)),", ",toString(round(upr,2)),"]"), col=4)
}
plotDistribution(2)   #succeeded
plotDistribution(3)   #skipped
md$total <- md$succeeded + md$skipped
plotDistribution(52)  #total downloaded

#THESE ABOVE ARE THE DISTRIBUTION OF ARTICLE GRAPHS APPEARING IN THE RESULTS SECTION (the ones look like they were made by a child :) 


#display top twenty per source
succeedsources <- c(4,11,18,25,32,39)
l <- list()
for (a in succeedsources){ 
  o = order(md[,a],decreasing = TRUE)
  #print( head(md[o,c(1,46,47,48,a)],n=20), row.names= FALSE ) 
  #l[[a]] <- head(md[o,c(1,46,47,48,a)],n=20)    #for just top 20 
  l[[a]] <- md[o,c(1,46,47,48,a)]  
}
res <- cbind( l[[4]], l[[11]], l[[18]], l[[25]], l[[32]], l[[39]])
resx <- xtable(res)
print(resx, type="html")


#THESE ABOVE WERE USED TO CREATE THE SOURCE SIDE BY SIDE VIEW

#display zero 
library(ggplot2)
#http://www.cookbook-r.com/Graphs/Multiple_graphs_on_one_page_(ggplot2)/
multiplot <- function(..., plotlist=NULL, file, cols=1, layout=NULL) {
  # ggplot objects can be passed in ..., or to plotlist (as a list of ggplot objects)
  # - cols:   Number of columns in layout
  # - layout: A matrix specifying the layout. If present, 'cols' is ignored.
  #
  # If the layout is something like matrix(c(1,2,3,3), nrow=2, byrow=TRUE),
  # then plot 1 will go in the upper left, 2 will go in the upper right, and
  # 3 will go all the way across the bottom.
  #
  library(grid)
  # Make a list from the ... arguments and plotlist
  plots <- c(list(...), plotlist)  
  numPlots = length(plots)  
  # If layout is NULL, then use 'cols' to determine layout
  if (is.null(layout)) {
    # Make the panel
    # ncol: Number of columns of plots
    # nrow: Number of rows needed, calculated from # of cols
    layout <- matrix(seq(1, cols * ceiling(numPlots/cols)),
                     ncol = cols, nrow = ceiling(numPlots/cols))
  } 
  if (numPlots==1) {
    print(plots[[1]])  
  } else {
    # Set up the page
    grid.newpage()
    pushViewport(viewport(layout = grid.layout(nrow(layout), ncol(layout))))
    
    # Make each plot, in the correct location
    for (i in 1:numPlots) {
      # Get the i,j matrix positions of the regions that contain this subplot
      matchidx <- as.data.frame(which(layout == i, arr.ind = TRUE))
      
      print(plots[[i]], vp = viewport(layout.pos.row = matchidx$row,
                                      layout.pos.col = matchidx$col))
    }
  }
}


makebar <- function(name,row,yl){
  dat <- data.frame(
    news_source = as.factor(c("aas","dmn","hc","nyt","txob","txtrb")),
    num_articles = row
  )
  ggplot(data=dat, aes(x=news_source, y=num_articles, fill=news_source)) + geom_bar(stat="identity") + ggtitle(name) + guides(fill=FALSE) + theme(axis.title.x = element_blank()) + ylab(yl) 
  
}

ss <- succeedsources
#bar chart of average articles per source per person, max
m1 <- makebar("Average Articles Per Person",c(mean(md[,ss[1]]),mean(md[,ss[2]]),mean(md[,ss[3]]),mean(md[,ss[4]]),mean(md[,ss[5]]),mean(md[,ss[6]])),"number of articles")
#m2 <- makebar("Max Articles Per Person",c(max(md[,ss[1]]),max(md[,ss[2]]),max(md[,ss[3]]),max(md[,ss[4]]),max(md[,ss[5]]),max(md[,ss[6]])),"")
m2 <- makebar("Median Articles Per Person",c(median(md[,ss[1]]),median(md[,ss[2]]),median(md[,ss[3]]),median(md[,ss[4]]),median(md[,ss[5]]),median(md[,ss[6]])),"")
m3 <- makebar("Standard Deviation of Articles Per Person",c(sd(md[,ss[1]]),sd(md[,ss[2]]),sd(md[,ss[3]]),sd(md[,ss[4]]),sd(md[,ss[5]]),sd(md[,ss[6]])),"")
multiplot(m1,m2,m3, cols=3)
  
#THE ABOVE WAS USED TO CREATE THE GGPLOT results-aricles-per person

#show how newspapers report based on party over level type
library(reshape2)
## i'd like one that showed (  state reps,   state senators,   combined )
##                          (  federal reps, federal senators, state-elected)  #so two rows of people

md.subone = md[which(md$level == "statewide-active"),c(1,47,48,4,11,18,25,32,39)]  #now instead of holding level, hold position 47
md.longone <- melt(md.subone, id.vars=c("name","position","party"))
md36 <- data.frame(matrix(ncol=4,nrow=36))
colnames(md36) <- c("position","party","variable","value")
md36$position <- c(rep("Representative",12),rep("Senator",12),rep("Together",12))
md36$party <- rep(c("Democrat","Republican"),18)
md36$variable <- c(rep(c("aas_succeed"),2),rep(c("dmn_succeed"),2),rep(c("hc_succeed"),2),rep(c("nyt_succeed"),2),rep(c("txob_succeed"),2),rep(c("txtr_succeed"),2),
                   rep(c("aas_succeed"),2),rep(c("dmn_succeed"),2),rep(c("hc_succeed"),2),rep(c("nyt_succeed"),2),rep(c("txob_succeed"),2),rep(c("txtr_succeed"),2),
                   rep(c("aas_succeed"),2),rep(c("dmn_succeed"),2),rep(c("hc_succeed"),2),rep(c("nyt_succeed"),2),rep(c("txob_succeed"),2),rep(c("txtr_succeed"),2))

for(i in 1:24){ md36[i,4] = sum(md.longone[which(md.longone$position == md36[i,1] & md.longone$party == md36[i,2] & md.longone$variable == md36[i,3]), 5]) }  
for(i in 1:12){ md36[i+24,4] <- md36[i,4] + md36[i+12,4]}  
ggplot(md36,aes(variable,value,fill=as.factor(party)))+ geom_bar(position="dodge",stat="identity")+ facet_wrap(~position,nrow=1) + theme(plot.title = element_text(face="bold", size=40), axis.title.x = element_text(face="bold", colour="#990000", size=30), axis.text.x  = element_text(angle=0, vjust=0.5, size=10)) + xlab("") + scale_x_discrete(breaks=c("aas_succeed", "dmn_succeed", "hc_succeed","nyt_succeed","txob_succeed","txtr_succeed"), labels=c("AAS", "DMN", "HC", "NYT", "TXOB", "TXTR")) + ylab("number of articles") 

#THE ABOVE WAS USED TO CREATE results-media-State-Rep-Sen-Together

md.fedreps <- md[which(md$level == "federal-active" ),c(1,47,48,4,11,18,25,32,39)]
md.source <- melt(md.fedreps, id.vars=c("name","position","party"))
ggplot(md.source,aes(variable,value,fill=as.factor(party)))+ geom_bar(position="dodge",stat="identity")+ facet_wrap(~position,nrow=1) + theme(plot.title = element_text(face="bold", size=40), axis.title.x = element_text(face="bold", colour="#990000", size=30), axis.text.x  = element_text(angle=0, vjust=0.5, size=10)) + xlab("") + scale_x_discrete(breaks=c("aas_succeed", "dmn_succeed", "hc_succeed","nyt_succeed","txob_succeed","txtr_succeed"), labels=c("AAS", "DMN", "HC", "NYT", "TXOB", "TXTR")) + ylab("number of articles") 

md.stateelected <- md[which(md$level == "statewide-active-elected"),c(1,47,48,4,11,18,25,32,39)]
md.source <- melt(md.stateelected, id.vars=c("name","party","position"))
ggplot(md.source,aes(variable,value,fill=as.factor(party)))+ geom_bar(position="dodge",stat="identity")+ facet_wrap(~party,nrow=1) + theme(plot.title = element_text(face="bold", size=40), axis.title.x = element_text(face="bold", colour="#990000", size=30), axis.text.x  = element_text(angle=0, vjust=0.5, size=10)) + xlab("") + scale_x_discrete(breaks=c("aas_succeed", "dmn_succeed", "hc_succeed","nyt_succeed","txob_succeed","txtr_succeed"), labels=c("AAS", "DMN", "HC", "NYT", "TXOB", "TXTR")) + ylab("number of articles") 

md.statesenate <- md[which(md$level == "statewide-active" & md$position == "Senator"),c(1,47,48,4,11,18,25,32,39)]
md.source <- melt(md.statesenate, id.vars=c("name","position","party"))
ggplot(md.source,aes(variable,value,fill=as.factor(party)))+ geom_bar(position="dodge",stat="identity")+ facet_wrap(~position,nrow=1) + theme(plot.title = element_text(face="bold", size=40), axis.title.x = element_text(face="bold", colour="#990000", size=30), axis.text.x  = element_text(angle=0, vjust=0.5, size=10)) + xlab("") + scale_x_discrete(breaks=c("aas_succeed", "dmn_succeed", "hc_succeed","nyt_succeed","txob_succeed","txtr_succeed"), labels=c("AAS", "DMN", "HC", "NYT", "TXOB", "TXTR")) + ylab("number of articles") 


#THE ABOVE WAS USED TO CREATE results-texasselect-federal-correctsize


#Distribution of Each Source
q1 <- qplot(md[,4]) + geom_bar(fill=colors()[4*30]) +ggtitle("Austin American Statesman") + guides(fill=FALSE) + xlab("") + ylab("Politicians")
q2 <- qplot(md[,11]) + geom_bar(fill=colors()[11*30]) +ggtitle("Dallas Morning News") + guides(fill=FALSE) + xlab("Articles Processed") + ylab("Politicians")
q3 <- qplot(md[,18]) + geom_bar(fill=colors()[18*30]) +ggtitle("Houston Chronicle") + guides(fill=FALSE) + xlab("") + ylab("")
q4 <- qplot(md[,25]) + geom_bar(fill=colors()[25*30]) +ggtitle("New York Times") + guides(fill=FALSE) + xlab("Articles Processed") + ylab("")
q5 <- qplot(md[,32]) + geom_bar(fill=colors()[32*30]) +ggtitle("Texas Observer") + guides(fill=FALSE) + xlab("") + ylab("")
q6 <- qplot(md[,39]) + geom_bar(fill=colors()[39*30]) +ggtitle("Texas Tribune") + guides(fill=FALSE) + xlab("Articles Processed") + ylab("")
multiplot(q1,q2,q3,q4,q5,q6, cols=3)
#no no this is ugly, but it works? 




md.statesenate <- md[which(md$level == "statewide-active" & md$position == "Senator"),c(1,47,48,4,11,18,25,32,39)]
md.source <- melt(md.statesenate, id.vars=c("name","position","party"))
md.source$name <- factor(md.source$name, levels = sort(md.source$name,decreasing = TRUE))
q1 <- ggplot(md.source, aes(x = name)) + geom_bar(aes(weight=value, fill = variable), position = 'fill') + ggtitle("Texas State Senators") + theme(axis.text.y = element_text(size=12,colour="black")) + coord_flip() + scale_fill_discrete(breaks=c("aas_succeed", "dmn_succeed", "hc_succeed","nyt_succeed","txob_succeed","txtr_succeed"), labels=c("AAS", "DMN", "HC", "NYT", "TXOB", "TXTR")) 

md.fedreps <- md[which(md$level == "federal-active" ),c(1,47,48,4,11,18,25,32,39)]
md.source <- melt(md.fedreps, id.vars=c("name","position","party"))
md.source$name <- factor(md.source$name, levels = sort(md.source$name,decreasing = TRUE))
q2 <- ggplot(md.source, aes(x = name)) + geom_bar(aes(weight=value, fill = variable), position = 'fill') + ggtitle("Federal Texan Congressmen") + theme(axis.text.y = element_text(size=12,colour="black")) + coord_flip() + scale_fill_discrete(breaks=c("aas_succeed", "dmn_succeed", "hc_succeed","nyt_succeed","txob_succeed","txtr_succeed"), labels=c("AAS", "DMN", "HC", "NYT", "TXOB", "TXTR")) 

md.stateelected <- md[which(md$level == "statewide-active-elected"),c(1,47,48,4,11,18,25,32,39)]
md.source <- melt(md.stateelected, id.vars=c("name","position","party"))
md.source$name <- factor(md.source$name, levels = sort(md.source$name,decreasing = TRUE))
q3 <- ggplot(md.source, aes(x = name)) + geom_bar(aes(weight=value, fill = variable), position = 'fill') + ggtitle("Texas Elected Officials") + theme(axis.text.y = element_text(size=12,colour="black")) + coord_flip() + scale_fill_discrete(breaks=c("aas_succeed", "dmn_succeed", "hc_succeed","nyt_succeed","txob_succeed","txtr_succeed"), labels=c("AAS", "DMN", "HC", "NYT", "TXOB", "TXTR")) 

md.statereps <- md[which(md$level == "statewide-active" & md$position == "Representative"),c(1,47,48,4,11,18,25,32,39)]

md.staterepsone <- md.statereps[1:49,]
md.source <- melt(md.staterepsone, id.vars=c("name","position","party"))
md.source$name <- factor(md.source$name, levels = sort(md.source$name,decreasing = TRUE))
q4 <- ggplot(md.source, aes(x = name)) + geom_bar(aes(weight=value, fill = variable), position = 'fill') + ggtitle("Texas State Reps") + theme(axis.text.y = element_text(size=12,colour="black")) + coord_flip() + scale_fill_discrete(breaks=c("aas_succeed", "dmn_succeed", "hc_succeed","nyt_succeed","txob_succeed","txtr_succeed"), labels=c("AAS", "DMN", "HC", "NYT", "TXOB", "TXTR")) 

md.staterepstwo <- md.statereps[50:99,]
md.source <- melt(md.staterepstwo, id.vars=c("name","position","party"))
md.source$name <- factor(md.source$name, levels = sort(md.source$name,decreasing = TRUE))
q5 <- ggplot(md.source, aes(x = name)) + geom_bar(aes(weight=value, fill = variable), position = 'fill') + ggtitle("Texas State Reps") + theme(axis.text.y = element_text(size=12,colour="black")) + coord_flip() + scale_fill_discrete(breaks=c("aas_succeed", "dmn_succeed", "hc_succeed","nyt_succeed","txob_succeed","txtr_succeed"), labels=c("AAS", "DMN", "HC", "NYT", "TXOB", "TXTR")) 

md.staterepsthree <- md.statereps[100:150,]
md.source <- melt(md.staterepsthree, id.vars=c("name","position","party"))
md.source$name <- factor(md.source$name, levels = sort(md.source$name,decreasing = TRUE))
q6 <- ggplot(md.source, aes(x = name)) + geom_bar(aes(weight=value, fill = variable), position = 'fill') + ggtitle("Texas State Reps") + theme(axis.text.y = element_text(size=12,colour="black")) + coord_flip() + scale_fill_discrete(breaks=c("aas_succeed", "dmn_succeed", "hc_succeed","nyt_succeed","txob_succeed","txtr_succeed"), labels=c("AAS", "DMN", "HC", "NYT", "TXOB", "TXTR")) 

#multiplot(q1,q2,q3,q4,q5,q6, cols=6)  #doesn't work
q1   #state senators
q2   #federal house/senate
q3   #state wide elected
q4   #1/3 state reps
q5   #2/3 state reps
q6   #3/3 state reps
plot(1:400,rep(0,400),xaxt="n", yaxt="n", xlim=c(0,400, ylim=c(0,400), xlab="",type="n"))
#THE ABOVE WAS TO CREATE THE TWO PAGE BIG IMAGES OF INDIVIDUALS

#aggregate for texas senate
#{AAS: 2868, DMN: 1542, HC: 7725, NYT: 314, TXOB: 893, TXTR: 4661}
texas_senate_multiplier <- list("AAS"= 2.69 , "DMN"= 5.01, "HC"= 1, "NYT"= 24.60, "TXOB"= 8.65, "TXTR"= 1.657 )
#now make scaled versions
#state senate 
md.statesenate.scaled <- md[which(md$level == "statewide-active" & md$position == "Senator"),c(1,47,48,4,11,18,25,32,39)]
sums <- colSums(md.statesenate.scaled[,4:9])
# aas_succeed  dmn_succeed   hc_succeed  nyt_succeed txob_succeed txtr_succeed 
# 2868         1542         7725          314          893         4661 
multiplier <- max(sums) / sums
# aas_succeed  dmn_succeed   hc_succeed  nyt_succeed txob_succeed txtr_succeed    #same as above so we are good for state senators 
# 2.693515     5.009728     1.000000    24.601911     8.650616     1.657370 
'''
md.statesenate.scaled$aas_succeed <- md.statesenate.scaled$aas_succeed * texas_senate_multiplier$AAS
md.statesenate.scaled$dmn_succeed <- md.statesenate.scaled$dmn_succeed * texas_senate_multiplier$DMN
md.statesenate.scaled$nyt_succeed <- md.statesenate.scaled$dmn_succeed * texas_senate_multiplier$NYT
md.statesenate.scaled$txob_succeed <- md.statesenate.scaled$dmn_succeed * texas_senate_multiplier$TXOB
md.statesenate.scaled$txtr_succeed <- md.statesenate.scaled$dmn_succeed * texas_senate_multiplier$TXTR
'''
md.statesenate.scaled[,4:9] <- md.statesenate.scaled[,4:9] * multiplier

md.source <- melt(md.statesenate.scaled, id.vars=c("name","position","party"))
md.source$name <- factor(md.source$name, levels = sort(md.source$name,decreasing = TRUE))
q1 <- ggplot(md.source, aes(x = name)) + geom_bar(aes(weight=value, fill = variable), position = 'fill') + ggtitle("Texas State Senators") + theme(axis.text.y = element_text(size=12,colour="black")) + coord_flip() + scale_fill_discrete(breaks=c("aas_succeed", "dmn_succeed", "hc_succeed","nyt_succeed","txob_succeed","txtr_succeed"), labels=c("AAS", "DMN", "HC", "NYT", "TXOB", "TXTR")) 
q1


federal_multiplier  <- list("AAS"= 6.63 , "DMN"= 7.43, "HC"= 1, "NYT"= 10.925, "TXOB"= 35.846, "TXTR"= 4.183 )
md.fedreps.scaled <- md[which(md$level == "federal-active"),c(1,47,48,4,11,18,25,32,39)]
sums <- colSums(md.fedreps.scaled[c(1:13,15:35,37,38),4:9])
# aas_succeed  dmn_succeed   hc_succeed  nyt_succeed txob_succeed txtr_succeed 
#        1962         1751        13012         1191          363         3111 
multiplier <- max(sums) / sums
# aas_succeed  dmn_succeed   hc_succeed  nyt_succeed txob_succeed txtr_succeed 
# 6.632008     7.431182     1.000000    10.925273    35.845730     4.182578  

'''
md.fedreps.scaled$aas_succeed <- md.fedreps.scaled$aas_succeed * federal_multiplier$AAS
md.fedreps.scaled$dmn_succeed <- md.fedreps.scaled$dmn_succeed * federal_multiplier$DMN
md.fedreps.scaled$nyt_succeed <- md.fedreps.scaled$dmn_succeed * federal_multiplier$NYT
md.fedreps.scaled$txob_succeed <- md.fedreps.scaled$dmn_succeed * federal_multiplier$TXOB
md.fedreps.scaled$txtr_succeed <- md.fedreps.scaled$dmn_succeed * federal_multiplier$TXTR
'''
md.fedreps.scaled[,4:9] <- md.fedreps.scaled[,4:9] * multiplier

#fix for ted cruz and john cornyn since these numbers are for reps and not senators
ted_cruz    <- c(639, 88,	693,	817,	65,	1316)  
john_cornyn <- c(498, 94,	784,	465,	86,	 694)  
fed_tots <- ted_cruz + john_cornyn
#               1137,182,1477, 1282, 151, 2010)
max_fed <- 2010
fed_sen_mult <- max_fed / fed_tots
md.fedreps.scaled[which(md.fedreps.scaled$name == "Ted Cruz"),4:9] <- ted_cruz * fed_sen_mult
md.fedreps.scaled[which(md.fedreps.scaled$name == "John Cornyn"),4:9] <- john_cornyn * fed_sen_mult

md.source <- melt(md.fedreps.scaled, id.vars=c("name","position","party"))
md.source$name <- factor(md.source$name, levels = sort(md.source$name,decreasing = TRUE))
q2 <- ggplot(md.source, aes(x = name)) + geom_bar(aes(weight=value, fill = variable), position = 'fill') + ggtitle("Federal Texan Congressmen") + theme(axis.text.y = element_text(size=12,colour="black")) + coord_flip() + scale_fill_discrete(breaks=c("aas_succeed", "dmn_succeed", "hc_succeed","nyt_succeed","txob_succeed","txtr_succeed"), labels=c("AAS", "DMN", "HC", "NYT", "TXOB", "TXTR")) 
q2


md.stateelected.scaled <- md[which(md$level == "statewide-active-elected"),c(1,47,48,4,11,18,25,32,39)]
sums <- colSums(md.stateelected.scaled[,4:9])
multiplier <- max(sums) / sums
# aas_succeed  dmn_succeed   hc_succeed  nyt_succeed txob_succeed txtr_succeed 
#    1.344605     5.103912     1.000000     5.085262    10.900783     1.507765 
md.stateelected.scaled[,4:9] <- md.stateelected.scaled[,4:9] * multiplier

md.source <- melt(md.stateelected.scaled, id.vars=c("name","position","party"))
md.source$name <- factor(md.source$name, levels = sort(md.source$name,decreasing = TRUE))
q3 <- ggplot(md.source, aes(x = name)) + geom_bar(aes(weight=value, fill = variable), position = 'fill') + ggtitle("Texas Elected Officials") + theme(axis.text.y = element_text(size=12,colour="black")) + coord_flip() + scale_fill_discrete(breaks=c("aas_succeed", "dmn_succeed", "hc_succeed","nyt_succeed","txob_succeed","txtr_succeed"), labels=c("AAS", "DMN", "HC", "NYT", "TXOB", "TXTR")) 
q3

#texas_house_multiplier  <- list("AAS"= 3.81 , "DMN"= 4.41, "HC"= 1, "NYT"= 27.796, "TXOB"= 9.84, "TXTR"= 1.605 )
thm <- c(3.81,4.41,1,27.796,9.84,1.605)
md.statereps <- md[which(md$level == "statewide-active" & md$position == "Representative"),c(1,47,48,4,11,18,25,32,39)]
# aas_succeed  dmn_succeed   hc_succeed  nyt_succeed txob_succeed txtr_succeed 
#        1302          972         5470          151          535         2806

md.staterepsone <- md.statereps[1:49,]
sums <- colSums(md.staterepsone[,4:9])
# aas_succeed  dmn_succeed   hc_succeed  nyt_succeed txob_succeed txtr_succeed 
#        1302          972         5470          151          535         2806 
multiplier <- max(sums) / sums
# aas_succeed  dmn_succeed   hc_succeed  nyt_succeed txob_succeed txtr_succeed 
#    4.201229     5.627572     1.000000    36.225166    10.224299     1.949394
#multiplier not the same as thm but relatively close

md.staterepsone[,4:9] <- md.staterepsone[,4:9] * multiplier
md.source <- melt(md.staterepsone, id.vars=c("name","position","party"))
md.source$name <- factor(md.source$name, levels = sort(md.source$name,decreasing = TRUE))
q4 <- ggplot(md.source, aes(x = name)) + geom_bar(aes(weight=value, fill = variable), position = 'fill') + ggtitle("Texas State Reps") + theme(axis.text.y = element_text(size=12,colour="black")) + coord_flip() + scale_fill_discrete(breaks=c("aas_succeed", "dmn_succeed", "hc_succeed","nyt_succeed","txob_succeed","txtr_succeed"), labels=c("AAS", "DMN", "HC", "NYT", "TXOB", "TXTR")) 
q4

md.staterepstwo <- md.statereps[50:99,]
sums <- colSums(md.staterepstwo[,4:9])
multiplier <- max(sums) / sums
md.staterepstwo[,4:9] <- md.staterepstwo[,4:9] * multiplier
md.source <- melt(md.staterepstwo, id.vars=c("name","position","party"))
md.source$name <- factor(md.source$name, levels = sort(md.source$name,decreasing = TRUE))
q5 <- ggplot(md.source, aes(x = name)) + geom_bar(aes(weight=value, fill = variable), position = 'fill') + ggtitle("Texas State Reps") + theme(axis.text.y = element_text(size=12,colour="black")) + coord_flip() + scale_fill_discrete(breaks=c("aas_succeed", "dmn_succeed", "hc_succeed","nyt_succeed","txob_succeed","txtr_succeed"), labels=c("AAS", "DMN", "HC", "NYT", "TXOB", "TXTR")) 
q5

md.staterepsthree <- md.statereps[100:150,]
sums <- colSums(md.staterepsthree[,4:9])
multiplier <- max(sums) / sums
md.staterepsthree[,4:9] <- md.staterepsthree[,4:9] * multiplier
md.source <- melt(md.staterepsthree, id.vars=c("name","position","party"))
md.source$name <- factor(md.source$name, levels = sort(md.source$name,decreasing = TRUE))
q6 <- ggplot(md.source, aes(x = name)) + geom_bar(aes(weight=value, fill = variable), position = 'fill') + ggtitle("Texas State Reps") + theme(axis.text.y = element_text(size=12,colour="black")) + coord_flip() + scale_fill_discrete(breaks=c("aas_succeed", "dmn_succeed", "hc_succeed","nyt_succeed","txob_succeed","txtr_succeed"), labels=c("AAS", "DMN", "HC", "NYT", "TXOB", "TXTR")) 
q6

