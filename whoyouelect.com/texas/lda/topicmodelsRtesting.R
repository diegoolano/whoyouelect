#topic models
#http://cran.r-project.org/web/packages/topicmodels/vignettes/topicmodels.pdf
#and http://www.jstatsoft.org/v40/i13/

#install.packages("topicmodels")
library("topicmodels")

#The latent Dirichlet allocation (LDA; Blei, Ng, and Jordan 2003b) model is a Bayesian mixture model 
#    for discrete data where topics are assumed to be uncorrelated.

#The correlated topics model (CTM; Blei and Lafferty 2007) is an extension of the LDA model where correlations between topics are allowed.

#The method used for fitting the models is the variational expectation-maximization (VEM) algorithm.

#install.packages("corpus.JSS.papers", repos = "http://datacube.wu.ac.at/", type = "source")

#1) load data for example
data("JSS_papers", package = "corpus.JSS.papers")

  dim(JSS_papers)    #636 by 15   .. 636 documents with 15 variables
  typeof(JSS_papers)  #list

  #to see row 1
  JSS_papers[1,1:15]
  '''
  $title      [1] "A Diagnostic to Assess the Fit of a Variogram Model to Spatial Data"
  $creator    [1] "Ronald Barry"
  $subject    [1] "Statistics" "Software"  
  $description[1] "The fit of a variogram model to spatially-distributed data is often difficult to assess. A graphical diagnostic written in S-plus is introduced that allows the user to determine both the general quality of the fit of a variogram model, and to find specific pairs of locations that do not have measurements that are consonant with the fitted variogram. It can help identify nonstationarity, outliers, and poor variogram fit in general. Simulated data sets and a set of soil nitrogen concentration data are examined using this graphical diagnostic."
  $publisher  [1] "Journal of Statistical Software"
  $contributor    character(0)
  $date       [1] "1996-08-16"
  $type       [1] "Text"     "Software" "Dataset" 
  $format         character(0)
  $identifier [1] "http://www.jstatsoft.org/v01/i01"
  $source     [1] "http://www.jstatsoft.org/v01/i01/paper"
  $language        character(0)
  $relation        character(0)
  $coverage        character(0)
  $rights          character(0)
  '''

#2) For reproducibility of results we use only abstracts published up to 2010-08-05 
#   and omit those containing non-ASCII characters in the abstracts
JSS_papers <- JSS_papers[JSS_papers[,"date"] < "2010-08-05",]
JSS_papers <- JSS_papers[sapply(JSS_papers[, "description"], Encoding) == "unknown",]

  dim(JSS_papers)  #348  15.  The final data set contains 348 documents.

#3) Before analysis we transform it to a "Corpus" using package tm. 
#HTML markup in the abstracts for greek letters, subscripting, etc., is removed using package XML
library("tm")
library("XML")
remove_HTML_markup <- function(s) 
                        tryCatch({
                          doc <- htmlTreeParse(paste("<!DOCTYPE html>", s), asText = TRUE, trim = FALSE)
                          xmlValue(xmlRoot(doc))
                        }, error = function(s) s)

corpus <- Corpus(VectorSource(sapply(JSS_papers[, "description"], remove_HTML_markup)))            
  length(corpus)   #348 documents
  typeof(corpus)   #list
  corpus[1]
      #<<VCorpus>>
      # Metadata:  corpus specific: 0, document level (indexed): 0
      # Content:  documents: 1  
  str(corpus[[1]])
      # List of 1
      # $ 1:List of 2
      # ..$ content: chr "The fit of a variogram model to spatially-distributed data is often difficult to assess. A graphical diagnostic written in S-pl"| __truncated__
      # ..$ meta   :List of 7
      # .. ..$ author       : chr(0) 
      # .. ..$ datetimestamp: POSIXlt[1:1], format: "2015-06-24 08:54:31"
      # .. ..$ description  : chr(0) 
      # .. ..$ heading      : chr(0) 
      # .. ..$ id           : chr "1"
      # .. ..$ language     : chr "en"
      # .. ..$ origin       : chr(0) 
      # .. ..- attr(*, "class")= chr "TextDocumentMeta"
      # ..- attr(*, "class")= chr [1:2] "PlainTextDocument" "TextDocument"
      # - attr(*, "class")= chr [1:2] "VCorpus" "Corpus"
  corpus[[1]]$content  #to see document 1 content
  corpus[[1]]$meta     #to see document 1 meta data



#4) The corpus is exported to a document-term matrix using function DocumentTermMatrix() from package tm. 
#   The terms are stemmed and the stop words, punctuation, numbers and
#   terms of length less than 3 are removed using the control argument. (We use a C locale for reproducibility.  ???)
            
Sys.setlocale("LC_COLLATE", "C")
#JSS_dtm <- DocumentTermMatrix(corpus, control = list(stemming = TRUE, stopwords = TRUE,
#                              minWordLength = 3, removeNumbers = TRUE, removePunctuation = TRUE))

# The above produces an error which doesn't occur if stemming isn't done
JSS_dtm <- DocumentTermMatrix(corpus, control = list(stopwords = TRUE, minWordLength = 3, removeNumbers = TRUE, removePunctuation = TRUE))
  
  dim(JSS_dtm)  #348 5022
  JSS_dtm[1,]
    # <<DocumentTermMatrix (documents: 1, terms: 5022)>>
    #   Non-/sparse entries: 39/4983                      #so doc 1 has 39 terms out of possible 4983
    # Sparsity           : 99%
    # Maximal term length: 36
    # Weighting          : term frequency (tf)
  JSS_dtm[1,1]$dimnames$Terms   #to see term at spot 1,1 <-- "abc"
  JSS_dtm$dimnames  #to see all terms (ie, columns)
  

#5) The mean term frequency-inverse document frequency (tf-idf) over documents containing this term is used to select the vocabulary. 
#   This measure allows to omit terms which have low frequency as well as those occurring in many documents! 
#   We only include terms which have a tf-idf value of at least 0.1 which is a bit more than the median and 
#   ensures that the very frequent terms are omitted.

  library("slam")
  summary(col_sums(JSS_dtm))  #each column is a word/term, and then this is to show how many times a word appears
  # Min. 1st Qu.  Median    Mean 3rd Qu.    Max.           #for instance, the avearge word appears 5.08 times, the most common appears 389
  #1.000   1.000   2.000   5.084   4.000 389.000 

term_tfidf <- tapply( JSS_dtm$v/row_sums(JSS_dtm)[JSS_dtm$i], JSS_dtm$j, mean) * log2( nDocs(JSS_dtm) / col_sums(JSS_dtm > 0))
#in the above, the first term is the term frequency matrix, while the second is the inverse document frequency

length(term_tfidf)     # 5022 terms
summary(term_tfidf)    # distribution of the term_tfidfs 
#   Min. 1st Qu.  Median    Mean 3rd Qu.    Max. 
#0.02285 0.07746 0.09933 0.12220 0.13620 1.16500

JSS_dtm <- JSS_dtm[,term_tfidf >= 0.1]   #only include those that have tfidf of .1
JSS_dtm <- JSS_dtm[row_sums(JSS_dtm) > 0,]  


  #After this pre-processing we have the following document-term matrix with a reduced vocabulary which we can use to fit topic models now!
  dim(JSS_dtm)   #348 2497    so we went from 5022 terms to 2497 terms !
  summary(col_sums(JSS_dtm))
  #  Min. 1st Qu.  Median    Mean 3rd Qu.    Max. 
  #1.000   1.000   1.000   2.687   3.000  35.000 


#6) In the following we fit an LDA model with 30 topics using 
#     (1) VEM with α estimated, 
#     (2) VEM with α fixed and 
#     (3) Gibbs sampling with a burn-in of 1000 iterations and recordingevery 100th iterations for 1000 iterations. 
#     (4) a CTM fitted using VEM estimation.
#   The initial α is set to the default value. 
#   By default only the best model with respect to the log-likelihood log(p(w|z)) observed during Gibbs sampling is returned. 

# We set the number of topics rather arbitrarily to 30 after investigating the performance with
# the number of topics varied from 2 to 200 using 10-fold cross-validation. The results indicated
# that the number of topics has only a small impact on the model fit on the hold-out data.
# There is only slight indication that the solution with two topics performs best and that the
# performance deteriorates again if the number of topics is more than 100. For applications a
# model with only two topics is of little interest because it enables only to group the documents very coarsely. 

# This lack of preference of a model with a reasonable number of topics might be due to the facts that 
#   (1) the corpus is rather small containing less than 500 documents and
#   (2) the corpus consists only of text documents on statistical software.

library("topicmodels")
k <- 30
SEED <- 2010   #for use with Gibbs sampling and CTM:  for reproducibility a random seed can be set which is used in the external code
jss_TM <- list(
              VEM       = LDA(JSS_dtm, k = k, control = list(seed = SEED)),
              VEM_fixed = LDA(JSS_dtm, k = k, control = list(estimate.alpha = FALSE, seed = SEED)),
              Gibbs     = LDA(JSS_dtm, k = k, method = "Gibbs", 
                                              control = list(seed = SEED, burnin = 1000, thin = 100, iter = 1000)),
              CTM       = CTM(JSS_dtm, k = k, control = list(seed = SEED, var = list(tol = 10^-4), em = list(tol = 10^-3))))


#7) To compare the fitted models we first investigate the α values of the models fitted 
#    (1) with VEM and α estimated and 
#    (2) with VEM and α fixed.
sapply(jss_TM[1:2], slot, "alpha")

#        VEM   VEM_fixed 
#0.007597997 1.666666667
#  We see that if α is estimated it is set to a value much smaller than the default of 1.6666. 
#  This indicates that in this case the Dirichlet distribution has more mass at the corners 
#  and hence, documents consist only of few topics!

#  The influence of α on the estimated topic distributions for documents is illustrated in Figure 1 (page 14 of pdf) 
#  where the probabilities of the assignment to the most likely topic for all documents are given. 

#  The lower α the higher is the percentage of documents which are assigned to one single topic with a high probability. 

#  Furthermore, it indicates that the association of documents with only one topic is strongest for the CTM solution.

#  The entropy measure can also be used to indicate how the topic distributions differ for the four fitting methods. 
#  We determine the mean entropy for each fitted model over the documents.

#  !!!
#  The term distribution for each topic as well as the predictive distribution of topics for a document 
#      can be obtained with posterior(). 
#      A list with components "terms" for the term distribution over topics and 
#                            "topics" for the topic distributions over documents is returned
sapply(jss_TM, function(x) mean(apply(posterior(x)$topics, 1, function(z) - sum(z * log(z)))))

#       VEM VEM_fixed     Gibbs       CTM 
# 0.1971858 3.0688715 3.2745341 0.1709847

# Higher values indicate that the topic distributions are more evenly spread over the topics.

# !!!
# The estimated topics for a document and estimated terms for a topic can be obtained using
# the convenience functions topics() and terms(). 

# Using the estimated alpha model(1), the most likely topic for each document is obtained by
Topic <- topics(jss_TM[["VEM"]], 1)

# Using the estimated alpha model(1), The five most frequent terms for each topic are obtained by
Terms <- terms(jss_TM[["VEM"]], 5)
Terms[,1:5]
  #       Topic 1      Topic 2 Topic 3       Topic 4    Topic 5    
  # [1,] "bayes"      "item"  "ordinal"     "genetic"  "formulae" 
  # [2,] "procedure"  "irt"   "categories"  "matrices" "formula"  
  # [3,] "robust"     "waved" "cell"        "risk"     "times"    
  # [4,] "spectra"    "rasch" "homogeneity" "factors"  "recursion"
  # [5,] "acceptance" "items" "impurity"    "mantel"   "sizes"    

#8) If any category labelings of the documents were available, these could be used to validate the fitted model. 
# Some JSS papers should have similar content because they appeared in the same special volume. 
# The most likely topic of the papers which appeared in Volume 24 
# called “Statistical Modeling of Social Networks with ‘statnet”’ is given by
(topics_v24 <- topics(jss_TM[["VEM"]])[grep("/v24/", JSS_papers[, "identifier"])])
# 243 244 245 246 247 248 249 250 251
#  21  25  21  21  27  21  21  23  21            #most of these papers are assigned topic 21
most_frequent_v24 <- which.max(tabulate(topics_v24))   

#The similarity between these papers is indicated by 
#the fact that the majority of the papers have the same topic as their most likely topic. 

#The ten most likely terms for topic 21 are given by
terms(jss_TM[["VEM"]], 10)[, most_frequent_v24]
  #"network" "ergm" "graph" "format" "econometr" "brief" "hydra" "statnet" "imag" "exponentialfamili"

# Clearly this topic is related to the general theme of the special issue. 
# This indicates that the fitted topic model was successful at detecting the similarity between papers in the same
# special issue without using this information.

