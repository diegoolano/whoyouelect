library(igraph)
?igraph

?read.graph
#http://cneurocvs.rmki.kfki.hu/igraphbook/igraphbook-foreign.html
G <- read.graph("/Users/dolano/htdocs/dama-larca/d3/whoyouelect-april27/netanalysis/andrew_murr.ncol",format="ncol")
G <- read.graph("/Users/dolano/htdocs/dama-larca/d3/whoyouelect-april27/netanalysis/john_smithee.ncol",format="ncol")

edrodcsv <- read.delim("/Users/dolano/htdocs/dama-larca/d3/whoyouelect-april27/netanalysis/eddie_rodriguezncol.csv",header = FALSE, sep = " ")
edcv <- edrodcsv[,1:3]
?write.csv
write.table(edcv, file="/Users/dolano/htdocs/dama-larca/d3/whoyouelect-april27/netanalysis/eddie_rodriguez-plain.ncol", row.names=FALSE, sep=" ", col.names=FALSE)

G <- read.graph("/Users/dolano/htdocs/dama-larca/d3/whoyouelect-april27/netanalysis/eddie_rodriguez-plain.ncol",format="ncol")


#CHECK IF PAGE RANK IS WORKING VIA BOBS NETWORK
bobcsv <- read.delim("/Users/dolano/htdocs/dama-larca/d3/whoyouelect-april27/netanalysis/bob_libalncol.csv",header = FALSE, sep = " ")
bobcv <- bobcsv[,1:3]
write.table(bobcv, file="/Users/dolano/htdocs/dama-larca/d3/whoyouelect-april27/netanalysis/bob_libal-plain.ncol", row.names=FALSE, sep=" ", col.names=FALSE)
G <- read.graph("/Users/dolano/htdocs/dama-larca/d3/whoyouelect-april27/netanalysis/bob_libal-plain.ncol",format="ncol")

#page rank correct in js!
#tested with http://localhost/dama-larca/d3/whoyouelect-april27/communities-from-ncol.html?s=Bob%20Libal&cl=25&t=.0001


#TODO MAKE shrink-python make an additional VERSION OF NCOL that we can read in here (can igraph.js run betweenness?)

G
#Andrew Murr
#IGRAPH UNW- 245 4859 -- 
#  + attr: name (v/c), weight (e/n)

#John Smithee
# IGRAPH UNW- 4161 499614 -- 
#   + attr: name (v/c), weight (e/n)

#Eddie Rodriguez
# IGRAPH UNW- 6226 572965 -- 
#   + attr: name (v/c), weight (e/n)

#Bob Libal
#IGRAPH UNW- 673 23643 -- 
#  + attr: name (v/c), weight (e/n)

V(G)$name
E(G)$weight

                          #Andrew Murr        #John Smithee     #Eddie Rodriguez    #Bob Libal
average.path.length(G)    #1.837              1.94              1.970433             1.89
diameter(G)               #4.6                1.1               5.5                  1
transitivity(G)           #0.946              .403              0.4701               0.5303923
mean(degree(G))           #39.66              240.14            184.05               70.26
degree(G)    #degree for each node
hist(degree(G))  #peaks around 1 and 96
hist(closeness(G))   #closeness centrality


#http://igraph.wikidot.com/community-detection-in-r

memberships <- list()
### edge.betweenness.community
ebc <- edge.betweenness.community(G)
mods <- sapply(0:ecount(G), function(i) {
  g2 <- delete.edges(G, ebc$removed.edges[seq(length=i)])
  cl <- clusters(g2)$membership
  modularity(G, cl)
})

g2 <- delete.edges(G, ebc$removed.edges[1:(which.max(mods)-1)])
memberships$`Edge betweenness` <- clusters(g2)$membership

#memberships   #found 3 clusters     ,    
#wc = modularity(memberships$`Edge betweenness`)
plot(G, vertex.color=clusters(g2)$membership)

### fastgreedy.community
fc <- fastgreedy.community(G)                        #for eddy rod.. length(unique(fc$membership)) = 30   and max(fc$modularity) = .62!!
memb <- community.to.membership(G, fc$merges,
                                steps=which.max(fc$modularity)-1)
memberships$`Fast greedy` <- memb$membership

dendPlot(fc )     #auto, phylo, dendrogram
dendPlot(fc, mode = "hclust")
dendPlot(fc, mode = "dendrogram")

### leading.eigenvector.community
lec <- leading.eigenvector.community(G)
memberships$`Leading eigenvector` <- lec$membership

#memberships     #found 6 clusters


### spinglass.community
sc <- spinglass.community(G, spins=10)
memberships$`Spinglass` <- sc$membership

#memberships     #found 7 clusters

### walktrap.community
wt <- walktrap.community(G, modularity=TRUE)
wmemb <- community.to.membership(G, wt$merges, steps=which.max(wt$modularity)-1)
memberships$`Walktrap` <- wmemb$membership

#memberships    #found 118 clusters

### label.propagation.community
memberships$`Label propagation` <- label.propagation.community(G)
plot(G, vertex.color=memberships$`Label propagation`$membership)

#memberships   #found 3

plot(G)
pg <- page.rank(G,directed = FALSE)

#FOR BOB
#> pg$vector[672]
#  184 
#  0.0005272639   <----

