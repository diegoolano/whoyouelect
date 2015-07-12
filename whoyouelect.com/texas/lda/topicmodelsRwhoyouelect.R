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

#1) load data for Eddie Rodriguez from a flight flight
#data("JSS_papers", package = "corpus.JSS.papers")

#  dim(JSS_papers)    #636 by 15   .. 636 documents with 15 variables
#  typeof(JSS_papers)  #list

  #to see row 1
#  JSS_papers[1,1:15]
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

eddr <- read.delim(file="/Users/dolano/htdocs/dama-larca/d3/whoyouelect-april27/lda/eddie_rodriguez-articles.tsv",header = T, sep="\t")
  typeof(eddr)     #"list"
  dim(eddr)        #"780 6"
  eddr[1:5,1:5] 
  #                                                              title       date         source  language   url   text
  # 1     Texas Inches to Tighter Rules 2 Years After Fertilizer Blast 2015-05-01 New York Times        en  ....
  # 2 Arming More Citizens to Fight Gun Violence in a Gun-Loving State 2012-12-21 New York Times        en  ....
  # 3                    Championing a Farm to Table Movement in Texas 2012-09-16 New York Times
  # 4                   Enforcement Is Next Task for Law on Wage Theft 2011-10-30 New York Times
  # 5                               DEMOCRATS VYING FOR HISPANIC VOTES 1987-06-29 New York Times
JSS_papers <- eddr

#2) For reproducibility of results we use only abstracts published up to 2010-08-05 
#   and omit those containing non-ASCII characters in the abstracts
#JSS_papers <- JSS_papers[JSS_papers[,"date"] < "2010-08-05",]
#JSS_papers <- JSS_papers[sapply(JSS_papers[, "description"], Encoding) == "unknown",]

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

corpus <- Corpus(VectorSource(sapply(JSS_papers[, "text"], remove_HTML_markup)))            
  length(corpus)   #780 documents
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
  
  dim(JSS_dtm)  #780 20567
  JSS_dtm[1,]
      # <<DocumentTermMatrix (documents: 1, terms: 20567)>>
      #   Non-/sparse entries: 224/20343                     #so first document has 224 terms
      # Sparsity           : 99%
      # Maximal term length: 172
      # Weighting          : term frequency (tf)
  JSS_dtm[1,1]$dimnames$Terms   #to see term at spot 1,1 <-- "abc"
  JSS_dtm$dimnames  #to see all terms (ie, columns)
  

#5) The mean term frequency-inverse document frequency (tf-idf) over documents containing this term is used to select the vocabulary. 
#   This measure allows to omit terms which have low frequency as well as those occurring in many documents! 
#   We only include terms which have a tf-idf value of at least 0.1 which is a bit more than the median and 
#   ensures that the very frequent terms are omitted.

  library("slam")
  summary(col_sums(JSS_dtm))  #each column is a word/term, and then this is to show how many times a word appears
  Min. 1st Qu.  Median    Mean 3rd Qu.    Max.      #for instance, the avarge word appears 16.08 times, the most common appears 3362
  1.00    1.00    2.00   16.68   10.00 3362.00 

term_tfidf <- tapply( JSS_dtm$v/row_sums(JSS_dtm)[JSS_dtm$i], JSS_dtm$j, mean) * log2( nDocs(JSS_dtm) / col_sums(JSS_dtm > 0))
#in the above, the first term is the term frequency matrix, while the second is the inverse document frequency

length(term_tfidf)     # 20567 terms
summary(term_tfidf)    # distribution of the term_tfidfs 
#     Min.  1st Qu.   Median     Mean  3rd Qu.     Max. 
# 0.001080 0.006584 0.013510 0.020350 0.022450 1.372000 

#cutoff <- 0.01
#cutoff <- 0.02    #what happens if i cutoff more aggressively
#cutoff <- 0.03
#cutoff <- 0.04
cutoff <- 0.05   


JSS_dtm <- JSS_dtm[,term_tfidf >= cutoff]   #only include those that have tfidf of .01  <--- THIS IS THE IMPORTANT NUMBER
JSS_dtm <- JSS_dtm[row_sums(JSS_dtm) > 0,]  


  #After this pre-processing we have the following document-term matrix with a reduced vocabulary which we can use to fit topic models now!
  dim(JSS_dtm)   
              #using cutoff 0.01 we get 780 12930    so we went from 20567 terms to 12930 terms !
              #using cutoff 0.02 we get 780 6501     so we went from 20567 terms to 6501 terms !
              #using cutoff 0.03 we get 780 3091
              #using cutoff 0.04 we get 717 1830
              #using cutoff 0.05 we get 695 1187
  summary(col_sums(JSS_dtm))
  #cutoff 0.01
  # Min. 1st Qu.  Median    Mean 3rd Qu.    Max. 
  #    1       1       2      15       9    3362  

  #cutoff 0.02
  #   Min. 1st Qu.  Median    Mean 3rd Qu.    Max. 
  #  1.000   1.000   2.000   9.424   5.000 849.000

  #cutoff 0.03
  #   Min. 1st Qu.  Median    Mean 3rd Qu.    Max. 
  #  1.000   1.000   2.000   9.335   5.000 849.000 

  #cutoff 0.04
  #  Min. 1st Qu.  Median    Mean 3rd Qu.    Max. 
  # 1.000   1.000   2.000   9.598   6.000 849.000

  #cutoff 0.05
  #   Min. 1st Qu.  Median    Mean 3rd Qu.    Max. 
  #  1.00    1.00    3.00   10.98    6.00  849.00 

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
k <- 20    #number of topics instead of 30, 10, try 20 <-- its all arbitrary anyways
SEED <- 2010   #for use with Gibbs sampling and CTM:  for reproducibility a random seed can be set which is used in the external code
jss_TM <- list( VEM       = LDA(JSS_dtm, k = k, control = list(seed = SEED)))   #if this goes slow try with Gibbs instead! 

#Gibbs and Vem give fairly similar results usually so don't worry
jss_GB <- list( Gibbs     = LDA(JSS_dtm, k = k, method = "Gibbs",  control = list(seed = SEED, burnin = 1000, thin = 100, iter = 1000)))
'''
              VEM_fixed = LDA(JSS_dtm, k = k, control = list(estimate.alpha = FALSE, seed = SEED)),
              Gibbs     = LDA(JSS_dtm, k = k, method = "Gibbs", 
                                              control = list(seed = SEED, burnin = 1000, thin = 100, iter = 1000)),
              CTM       = CTM(JSS_dtm, k = k, control = list(seed = SEED, var = list(tol = 10^-4), em = list(tol = 10^-3))))
'''

#7) To compare the fitted models we first investigate the α values of the models fitted 
#    (1) with VEM and α estimated and 
#    (2) with VEM and α fixed.
#sapply(jss_TM[1:2], slot, "alpha")

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

#sapply(jss_TM, function(x) mean(apply(posterior(x)$topics, 1, function(z) - sum(z * log(z)))))

#       VEM VEM_fixed     Gibbs       CTM 
# 0.1971858 3.0688715 3.2745341 0.1709847

# Higher values indicate that the topic distributions are more evenly spread over the topics.

# !!!
# The estimated topics for a document and estimated terms for a topic can be obtained using
# the convenience functions topics() and terms(). 

# Using the estimated alpha model(1), the most likely topic for each document is obtained by
Topic <- topics(jss_TM[["VEM"]], 1)
length(Topic)  #780  most likely topic for each document
library(ggplot2)
Topic <- as.factor(Topic)
makebar <- function(name,row){
  dat <- data.frame(
    topicc = as.factor(c(1:k)),
    documents = row
  )
  ggplot(data=dat, aes(x=topicc, y=documents, fill=topicc)) + geom_bar(stat="identity") + ggtitle(name) + guides(fill=FALSE)
}
makebar("topic assignment to documents distribution using VEM",Topic)     

#TopicG <- topics(jss_GB[["Gibbs"]], 1)
#TopicG <- as.factor(TopicG)
#makebar("topic assignment to documents distribution using Gibbs",Topic)

# Using the estimated alpha model(1), The FT most frequent terms for each topic are obtained by
FT <- 20
Terms <- terms(jss_TM[["VEM"]], 10)
#TermsG <- terms(jss_GB[["Gibbs"]],20)      #This just shows that both approaches give similar results.  They are similar timewise.
dim(Terms)
Terms[,1:10]    #with cutoff 0.01 and 10 topics top 5
#       Topic 1        Topic 2      Topic 3      Topic 4      Topic 5  Topic 6    Topic 7          Topic 8          Topic 9   Topic 10 
# [1,] "birkenstocks" "said"       "district"   "said"       "cheese" "school"   "said"           "texas"          "johnson" "slowik" 
# [2,] "wear"         "immigrants" "house"      "resolution" "ball"   "bill"     "texas"          "representative" "said"    "says"   
# [3,] "shoe"         "police"     "republican" "burnam"     "war"    "said"     "bill"           "said"           "man"     "chu"    
# [4,] "feet"         "williams"   "defeated"   "slowik"     "said"   "texas"    "house"          "house"          "macys"   "jacket" 
# [5,] "shoes"        "home"       "nomination" "house"      "taxes"  "students" "representative" "tax"            "tickets" "clothes"

TermsG[,1:10]   #gibss with cutoff 0.01 and 10 topics
#       Topic 1  Topic 2   Topic 3   Topic 4  Topic 5          Topic 6          Topic 7        Topic 8          Topic 9   Topic 10    
# [1,] "said"   "hours"   "johnson" "said"   "said"           "house"          "birkenstocks" "school"         "slowik"  "said"      
# [2,] "cheese" "earlier" "center"  "texas"  "house"          "district"       "wear"         "tax"            "says"    "police"    
# [3,] "ball"   "news"    "macys"   "bill"   "resolution"     "texas"          "feet"         "bill"           "chu"     "immigrants"
# [4,] "bonds"  "full"    "tickets" "austin" "representative" "republican"     "said"         "taxes"          "meyer"   "arrested"  
# [5,] "game"   "found"   "sept"    "law"    "support"        "representative" "shoe"         "representative" "fashion" "home"      


Terms[,1:10] #with cutoff 0.02 and 10 topics  <--- seems to be better
      # Topic 1  Topic 2      Topic 3   Topic 4     Topic 5     Topic 6    Topic 7     Topic 8       Topic 9        Topic 10 
# [1,] "cheese" "war"        "slowik"  "apartment" "district"  "energy"   "school"    "immigrants"  "birkenstocks" "court"  
# [2,] "ball"   "resolution" "jacket"  "arrested"  "county"    "dist"     "board"     "johnson"     "wear"         "judge"  
# [3,] "bonds"  "district"   "chu"     "officers"  "committee" "per"      "students"  "williams"    "feet"         "milford"
# [4,] "game"   "taxes"      "wear"    "school"    "craddick"  "diluted"  "districts" "brownsville" "shoe"         "school" 
# [5,] "jackie" "defeated"   "tickets" "leg"       "speaker"   "earnings" "taxes"     "tickets"     "birkenstock"  "dulin"    

Terms[,1:10] #for cutoff 0.03  <-- even better
#      Topic 1      Topic 2      Topic 3        Topic 4       Topic 5         Topic 6   Topic 7    Topic 8      Topic 9  Topic 10  
# [1,] "district"   "slowik"     "birkenstocks" "immigrants"  "tesla"         "jackie"  "district" "war"        "cheese" "dist"    
# [2,] "nomination" "tickets"    "shoe"         "williams"    "cbo"           "cassini" "board"    "resolution" "ball"   "pledges" 
# [3,] "defeated"   "macys"      "birkenstock"  "brownsville" "dealers"       "doll"    "craddick" "troops"     "bonds"  "silence" 
# [4,] "win"        "johnson"    "seniority"    "harlingen"   "manufacturers" "farmers" "straus"   "burnam"     "noon"   "hupp"    
# [5,] "fire"       "foundation" "arrested"     "victor"      "electric"      "farm"    "travis"   "policies"   "fri"    "abortion"

Terms[,1:10] #for cutoff 0.04 and 10 topics 
#       Topic 1       Topic 2       Topic 3          Topic 4      Topic 5      Topic 6        Topic 7      Topic 8   Topic 9     Topic 10   
# [1,] "straus"      "immigrants"  "seniority"      "war"        "foundation" "birkenstocks" "district"   "beach"   "dist"      "tesla"    
# [2,] "gambling"    "brownsville" "appropriations" "cheese"     "jackie"     "shoe"         "win"        "leg"     "gopst"     "cbo"      
# [3,] "breakfast"   "harlingen"   "dulin"          "resolution" "cassini"    "birkenstock"  "defeated"   "grams"   "mortgage"  "guns"     
# [4,] "sunday"      "victor"      "diluted"        "ball"       "doll"       "farmers"      "nomination" "heroin"  "demst"     "legate"   
# [5,] "census"      "seth"        "milford"        "bonds"      "pledges"    "farm"         "maps"       "noon"    "servicers" "solar"    
# [6,] "dubord"      "metro"       "earnings"       "policies"   "silence"    "markets"      "plaintiffs" "fri"     "minors"    "concealed"
# [7,] "katy"        "lane"        "probation"      "overseas"   "hupp"       "fitness"      "morales"    "seized"  "nov"       "yolanda"  
# [8,] "dec"         "sanctuary"   "nongaap"        "fire"       "boxer"      "dog"          "cervantes"  "sun"     "gopapp"    "dealers"  
# [9,] "fire"        "efficiency"  "gaap"           "ammonium"   "abortion"   "dogs"         "trustees"   "bradley" "bypass"    "renewable"
# [10,] "leffingwell" "epa"         "wearhouse"      "nitrate"    "error"      "producers"    "denton"     "mendoza" "hutto"     "handgun"     

Terms[,1:30] #for cuttoff 0.04 and 30 topics (only showing 20 topics)
#       Topic 1        Topic 2      Topic 3       Topic 4      Topic 5          Topic 6          Topic 7      Topic 8     Topic 9      Topic 10       
# [1,] "straus"       "efficiency" "dulin"       "war"        "district"       "fitness"        "district"   "beach"     "expenses"   "immigrants"   
# [2,] "katy"         "lane"       "probation"   "resolution" "morales"        "distributors"   "defeated"   "leg"       "relief"     "brownsville"  
# [3,] "sunday"       "solar"      "milford"     "policies"   "cervantes"      "kleinschmidt"   "nomination" "grams"     "incentives" "harlingen"    
# [4,] "win"          "renewable"  "bavedas"     "overseas"   "antifreeze"     "homestead"      "win"        "heroin"    "employers"  "victor"       
# [5,] "gambling"     "hightower"  "keefe"       "morale"     "trustees"       "feb"            "mcguinness" "bradley"   "courses"    "tesla"        
# [6,] "audubon"      "epa"        "cronan"      "payday"     "edgewood"       "craft"          "twoterm"    "rangers"   "orourke"    "dealers"      
# [7,] "preservation" "tsa"        "dulins"      "lenders"    "gibbs"          "brewers"        "unopposed"  "seized"    "chvez"      "musk"         
# [8,] "drops"        "metro"      "ideological" "defeated"   "sekula"         "brewing"        "victor"     "macmillan" "canseco"    "manufacturers"
# [9,] "incentives"   "permitting" "bridgeport"  "silence"    "superintendent" "metzger"        "toughest"   "mendoza"   "instate"    "dealerships"  
# [10,] "patients"     "fullbody"   "polygraph"   "norcross"   "renters"        "cardiovascular" "newcomers"  "sunday"    "homebuyers" "teslas"       

# Topic 11     Topic 12         Topic 13     Topic 14      Topic 15     Topic 16      Topic 17     Topic 18       Topic 19      Topic 20     
# [1,] "theft"      "legate"         "district"   "dist"        "foundation" "pledges"     "abortion"   "birkenstocks" "noon"        "sanctuary"  
# [2,] "metro"      "yolanda"        "maps"       "gopst"       "models"     "silence"     "abortions"  "shoe"         "fri"         "policies"   
# [3,] "campo"      "maddox"         "plaintiffs" "demst"       "aug"        "hupp"        "gay"        "birkenstock"  "sun"         "conferees"  
# [4,] "iaf"        "legates"        "seth"       "dogs"        "bypass"     "nov"         "marriage"   "cowboy"       "ave"         "tons"       
# [5,] "gala"       "dec"            "latino"     "dog"         "minors"     "leffingwell" "photoeric"  "marcus"       "monfri"      "lottery"    
# [6,] "cops"       "jury"           "compromise" "animal"      "yanez"      "lahood"      "admitting"  "abplanalp"    "tuessat"     "courses"    
# [7,] "grocery"    "stamps"         "maldef"     "gopapp"      "lab"        "wolff"       "dictate"    "advocated"    "photographs" "epa"        
# [8,] "graham"     "fingerprinting" "contests"   "uncontested" "dna"        "dry"         "pills"      "anchored"     "thurs"       "recabarren" 
# [9,] "interfaith" "restaurant"     "census"     "noble"       "parental"   "governance"  "privileges" "articles"     "appt"        "wils"       
# [10,] "becerra"    "sunday"         "trustees"   "declared"    "isi"        "nicolas"     "surgical"   "attempts"     "oakland"     "capandtrade"

Terms[,1:20]   #for cutoff 0.05 and 20 topics



summary(as.factor(Topic))     
#for cutoff 0.01 and 10 topics  #some topics are more important 7,8,9, followed by 6,3, but each one has a sizable number
#  1   2   3   4   5   6   7   8   9  10 
# 42  53  70  27  64  85 126 134 130  49

#for cutoff 0.02 and 20 topics.. still prety evenly distributed with more important being 9,14,17
#  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 
# 26 26 44 21 30 24 44 50 69 26 45 32 37 72 23 38 64 39 43 27 

#for cutoff 0.03 and 10 topics summary(as.factor(Topic))
# 1   2   3   4   5   6   7   8   9  10 
#57  96  80  54  91 126  93  90  28  65 

# for cuttoff 0.04 and 10 topics
# 1   2   3   4   5   6   7   8   9  10 
#76  69  66 103 156  64  65  29  31  58 

#for cuttoff 0.04 and 30 topics
#  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 
# 21 20 13 68 16 19 24 26 20 32 16 12 37  4 49 34 11 21  4 19 32  4 22 15 20 25 58 20 35 20


#8) If any category labelings of the documents were available, these could be used to validate the fitted model. 
# We don't have that since no articles don't come pre-labeled with topics in the realworld, however we do have date values
# and as such would expect articles from the same year to be more similar
topics_2013 <- topics(jss_TM[["VEM"]])[grep("2013", JSS_papers[, "date"])]
  length(topics_2013)   #found 75 articles

summary(as.factor(topics_2013))    #of these most are 6, 7, or 8
# 2  4  6  7  8  9 10              #for cutoff 0.01
# 3  1 15 26 22  7  1 

# 1  2  4  5  6  7  8  9 10        #for cutoff 0.02   6, 5, 7 most important 
# 4  1  6 19 20 11  6  1  7 

most_frequent_2013 <- which.max(tabulate(topics_2013))    #topic 7
second_most_frequent_2013 <- 5
third_most_frequent_2013  <- 7

importanttopics <- terms(jss_TM[["VEM"]], 50)[, c(most_frequent_2013,second_most_frequent_2013,third_most_frequent_2013)]
importanttopics
# the resulting topics overlap a lot!
#       Topic 7          Topic 8          Topic 6         
#  [1,] "said"           "texas"          "school"        
#  [2,] "texas"          "representative" "bill"          
#  [3,] "bill"           "said"           "said"          
#  [4,] "house"          "house"          "texas"         
#  [5,] "representative" "tax"            "students"      
#  [6,] "committee"      "republican"     "representative"
#  [7,] "members"        "austin"         "law"           
#  [8,] "austin"         "county"         "sat"           
#  [9,] "legislation"    "senate"         "ends"          
# [10,] "craddick"       "perry"          "schools"       
# [11,] "rules"          "republicans"    "day"           
# [12,] "allow"          "democrats"      "paintings"     
# [13,] "bills"          "chair"          "districts"     
# [14,] "vote"           "percent"        "senate"        
# [15,] "seniority"      "money"          "runs"          
# [16,] "chairman"       "school"         "noon"          
# [17,] "democrats"      "session"        "children"      
# [18,] "speaker"        "says"           "pledges"       
# [19,] "committees"     "antonio"        "measure"       
# [20,] "percent"        "districts"      "silence"   

#sorted 
cbind(sort(terms(jss_TM[["VEM"]], 20)[,c(7)]) , sort(terms(jss_TM[["VEM"]], 20)[,c(8)]), sort(terms(jss_TM[["VEM"]], 20)[,c(6)]))
#        TOPIC 7          TOPIC 8         TOPIC 6
#  [1,] "allow"          "antonio"        "bill"          
#  [2,] "austin"         "austin"         "children"      
#  [3,] "bill"           "chair"          "day"           
#  [4,] "bills"          "county"         "districts"     
#  [5,] "chairman"       "democrats"      "ends"          
#  [6,] "committee"      "districts"      "law"           
#  [7,] "committees"     "house"          "measure"       
#  [8,] "craddick"       "money"          "noon"          
#  [9,] "democrats"      "percent"        "paintings"     
# [10,] "house"          "perry"          "pledges"       
# [11,] "legislation"    "representative" "representative"
# [12,] "members"        "republican"     "runs"          
# [13,] "percent"        "republicans"    "said"          
# [14,] "representative" "said"           "sat"           
# [15,] "rules"          "says"           "school"        
# [16,] "said"           "school"         "schools"       
# [17,] "seniority"      "senate"         "senate"        
# [18,] "speaker"        "session"        "silence"       
# [19,] "texas"          "tax"            "students"      
# [20,] "vote"           "texas"          "texas" 

#removing overlap
#        TOPIC 7          TOPIC 8         TOPIC 6
#  [1,] "allow"          "antonio"                  
#  [2,]                                   "children"      
#  [3,]                  "chair"          "day"           
#  [4,] "bills"          "county"                
#  [5,] "chairman"                        "ends"          
#  [6,] "committee"                       "law"           
#  [7,] "committees"                      "measure"       
#  [8,] "craddick"       "money"          "noon"          
#  [9,]                                   "paintings"     
# [10,]                  "perry"          "pledges"       
# [11,] "legislation"    " 
# [12,] "members"        "republican"     "runs"          
# [13,]                  "republicans"              
# [14,]                                   "sat"           
# [15,] "rules"          "says"           
# [16,]                  
# [17,] "seniority"      
# [18,] "speaker"        "session"        "silence"       
# [19,]                  "tax"            "students"      
# [20,] "vote"           