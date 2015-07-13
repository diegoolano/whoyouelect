library("topicmodels")
library("tm")
library("XML")
library("slam")
library(RWeka)

### FUNCTIONS
remove_HTML_markup <- function(s) 
  tryCatch({
    doc <- htmlTreeParse(paste("<!DOCTYPE html>", s), asText = TRUE, trim = FALSE)
    xmlValue(xmlRoot(doc))
  }, error = function(s) s)

print.matrix <- function(m){
  write.table(format(m, justify="right"),
              row.names=TRUE, col.names=F, quote=F)
}

get_cutoffval_and_type <- function(term_tfidf,highend,lowend){
  cutoffval_type = ""
  third_quartile_cutoffval <- summary(term_tfidf)[[5]]
  potential_new_terms_length <- length(which(term_tfidf > third_quartile_cutoffval))
  if(potential_new_terms_length >= lowend & potential_new_terms_length < highend){     
    cutoff <- third_quartile_cutoffval
    cutoffval_type = "third_quartile_cutoffval"
  }else {
    if(potential_new_terms_length < lowend){
      #the cut was too aggressive so use mean
      mean_cutoffval <- mean(term_tfidf)
      potential_new_terms_length <- length(which(term_tfidf > mean_cutoffval))
      if(potential_new_terms_length >= lowend & potential_new_terms_length < highend){ 
          cutoff <- mean_cutoffval
          cutoffval_type = "mean_cutoffval"
      } else{
        if(potential_new_terms_length < lowend){
          #cut was too aggressive still, use median y ya
          cutoff <- median(term_tfidf)
          cutoffval_type = "median"
        }else{
          # so too weak so use midway point between third and mean as new val
          cutoff <- mean_cutoffval + ( (third_quartile_cutoffval - mean_cutoffval) / 2 )
          cutoffval_type = "midway_beteen_mean_and_third"
        }
      }
    } else{
      #the cut was too weak.. this could be because there are many many terms hmmm... be aggressive at first
      third_plus_mean_cutoffval <- summary(term_tfidf)[[5]] + mean(term_tfidf)
      potential_new_terms_length <- length(which(term_tfidf > third_plus_mean_cutoffval))
      if(potential_new_terms_length >= lowend & potential_new_terms_length < highend){ 
        cutoff <- third_plus_mean_cutoffval
        cutoffval_type = "third_plus_mean"
      }else{
        if(potential_new_terms_length < lowend){
          #too strong so bring it down and use third_plus_median
          third_plus_median_cutoffval <- summary(term_tfidf)[[5]] + median(term_tfidf)
          potential_new_terms_length <- length(which(term_tfidf > third_plus_median_cutoffval))
          if(potential_new_terms_length >= lowend & potential_new_terms_length < highend){ 
            cutoff <- third_plus_median_cutoffval
            cutoffval_type = "third_plus_median_cutoffval"
          }else{
            if(potential_new_terms_length < lowend){
              #still too strong so just use third_plus_first
              cutoff <- summary(term_tfidf)[[5]] + summary(term_tfidf)[[1]]
              cutoffval_type = "third_plus_first"
            }else{
              #too weak so use midway between mean and median ( unlikely)
              cutoff <- summary(term_tfidf)[[5]] + median(term_tfidf) + ( mean(term_tfidf) - median(term_tfidf))
              cutoffval_type = "third_plus_midway_between_mean_and_median"
            }
          }
        }else
        {
          #two first cuts were too weak so go with third + mean
          cutoff <- summary(term_tfidf)[[5]] + mean(term_tfidf)
          cutoffval_type = "third_plus_mean_cutoffval"
        }
        
      }
    }
  }
  list("cutoff"=cutoff, "cutoff_type"=cutoffval_type)
} 


runTopicModelingOn <- function(tsvfile,k,highend,lowend,path_to_tsvs,debug=FALSE){
  SEED <- 2010   #for reproducibility 
  #for every tsv in folder
  #pol_tsvfile = "/Users/dolano/htdocs/dama-larca/d3/whoyouelect-april27/lda/eddie_rodriguez-articles.tsv"
  pol_tsvfile = paste(path_to_tsvs,tsvfile,sep="")
  eddr <- suppressWarnings( read.delim(file=pol_tsvfile,header = T, sep="\t") )
  ps <- strsplit(pol_tsvfile,"/")
  entitynamefull <- ps[[1]][length(ps[[1]])]
  entityname <- strsplit(entitynamefull,"-articles.tsv")[[1]][1]
  
  dim(eddr)  #780 articles with 6 fields each
  if( nrow(eddr) > 0){ 
    
  JSS_papers <- eddr
  corpus <- Corpus(VectorSource(sapply(JSS_papers[, "text"], remove_HTML_markup)))      
  
  #BigramTokenizer <- function(x) unlist(lapply(ngrams(words(x), 2), paste, collapse = " "), use.names = FALSE)
  TrigramTokenizer <- function(x) unlist(lapply(ngrams(words(x), 3), paste, collapse = " "), use.names = FALSE)
  
  #JSS_dtm <- DocumentTermMatrix(corpus, control = list(stopwords = TRUE, minWordLength = 3, removeNumbers = TRUE, removePunctuation = TRUE)  #1 gram
  #JSS_dtm <- DocumentTermMatrix(corpus, control = list(stopwords = TRUE, minWordLength = 3, removeNumbers = TRUE, removePunctuation = TRUE, tokenize = BigramTokenizer)) #2gram
  JSS_dtm <- DocumentTermMatrix(corpus, control = list(stopwords = TRUE, minWordLength = 3, removeNumbers = TRUE, removePunctuation = TRUE, tokenize = TrigramTokenizer)) #3gram
  term_tfidf <- tapply( JSS_dtm$v/row_sums(JSS_dtm)[JSS_dtm$i], JSS_dtm$j, mean) * log2( nDocs(JSS_dtm) / col_sums(JSS_dtm > 0))
  number_of_initial_terms <- length(term_tfidf)
  
  cutoffvals <- get_cutoffval_and_type(term_tfidf,highend,lowend)
  cutoff <- cutoffvals$cutoff
  cutoff_type <- cutoffvals$cutoff_type                           
  JSS_dtm <- JSS_dtm[,term_tfidf >= cutoff]   #only include those that have tfidf of at least cutoff value
  JSS_dtm <- JSS_dtm[row_sums(JSS_dtm) > 0,]  #this removes empty documents ( ie, no terms found in them so sum of terms if zero)
  post_cutoff_terms <- ncol(JSS_dtm)
  #print(paste(entityname,nrow(eddr),number_of_initial_terms, cutoff, cutoff_type, nrow(JSS_dtm),post_cutoff_terms ))
  
  jss_TM <- list( VEM       = LDA(JSS_dtm, k = k, control = list(seed = SEED)))   #run Latent Dirichlet Allocation with values
  Topic <- topics(jss_TM[["VEM"]], 1)   #contains the most likely topic for each document.. length(Topic) is number of documents, k is number of topics
  Topic <- as.factor(Topic)
  Terms <- terms(jss_TM[["VEM"]], 10)   #top 10 most frequent terms for each topic are obtained, row is Topic, columns are terms
  
  if(debug == TRUE){
     print(Terms[1:10,1:20])  #shows top 10 terms for 20 topics
     print(sort(summary(as.factor(Topic)))) #to see spread of how many documents are associated with each topic
  }
  
  #HOW TO FIND ARTICLES ASSOCIATED WITH A TOPIC
  #which(Topic == 19)   #gives ids for documents associated with topic 19, then use eddr[which(Topic == 19),5] to get articles .. i think
  
  summary_topic <- summary(as.factor(Topic)) 
  most_frequent_topics <- as.numeric(names(sort(summary_topic,decreasing=TRUE)))
  most_frequent_topics_documents <- sapply(most_frequent_topics,function(a){ summary_topic[a][[1]]})  
  most_frequent_percents <- sapply(most_frequent_topics_documents,function(a){ round(100 * a / sum(summary_topic),2)})
  importanttopics <- terms(jss_TM[["VEM"]], 10)[,most_frequent_topics]
  importanttopics_withpercentaages <- rbind(most_frequent_percents,importanttopics)

  line <- paste(entityname,nrow(eddr),number_of_initial_terms, cutoff, cutoff_type, nrow(JSS_dtm),post_cutoff_terms )  
  print(line)
  fileout <- paste(path_to_tsvs,"SUMMARIZINGpoliticians-3grams.out",sep="")
  write(line,file=fileout,append=TRUE)  
  write.table(format(t(importanttopics_withpercentaages), justify="left"), file=fileout, append=TRUE,row.names=TRUE, col.names=F, quote=F,sep=",")
  }else{
    print(paste(entityname,"has no articles so don't include"))
  }
}



##START HERE
path_to_tsvs = "/Users/dolano/htdocs/dama-larca/d3/generate_network/data/tsvs/"
tsvfiles = dir(path_to_tsvs,pattern =".tsv")

#parameters to set
k <- 20    #number of topics
highend = 4000  #want less than this many terms
lowend = 2000   #want more than this many terms
#cutoff <- 0.04   #<-- this is set automatically based on the highend lowend terms

#to fix fuck ups "allen_fletcher-articles-fixed.tsv",
#tsvfiles = c("ana_hernandez-articles-fixed.tsv","borris_miles-articles-fixed.tsv")

for(tsvfile in tsvfiles){
  print(tsvfile)
  ptm <- proc.time()
  result <- tryCatch({
    runTopicModelingOn(tsvfile,k,highend,lowend,path_to_tsvs,debug=F)
    },warning = function(war){  
      print(paste("warning",war))
      return(0);
    },error = function(e){ 
      print(paste("error",e))
      return(0);
    },finally = {
      print(proc.time() - ptm)
    })  
}

tsvfile = "eddie_rodriguez-articles.tsv"
articlesForCommunity <- c("http://www.statesman.com/news/news/state-regional-govt-politics/urban-farmers-fight-to-be-treated-like-their-cou-1/nRnqy/", "2012-05-18", "6", "www.texastribune.org/2013/05/30/bipartisan-caucus-lays-groundwork-food-movement/", "2013-05-30", "6", "www.texastribune.org/2008/05/26/ghosts-and-other-scary-stuff/", "2008-05-26", "5", "www.texastribune.org/2005/01/31/it-never-hurts-to-ask/", "2005-01-31", "5", "www.texastribune.org/2002/09/16/off-to-the-races-1/", "2002-09-16", "5", "http://www.chron.com//business/local/article/Bipartisan-caucus-lays-groundwork-for-food-4563140.php", "2013-05-30", "5", "http://www.nytimes.com/2012/09/16/us/championing-a-farm-to-table-movement-in-texas.html", "2012-09-16", "3", "http://www.statesman.com/news/lifestyles/food-cooking/relish-austin-farmers-at-sxsw-eco-talk-about-why-f/nSYGJ/", "2012-10-09", "3", "http://www.statesman.com/news/news/state-regional-govt-politics/austin-legislator-cooking-up-foodie-caucus-1/nRnWp/", "2012-05-04", "3", "http://www.statesman.com/news/news/state-regional-govt-politics/travis-county-would-be-split-four-ways-under-sta-1/nRZyS/", "2011-05-11", "3", "http://www.statesman.com/news/news/local/dwi-charge-dropped-against-state-lawmaker-1/nRywP/", "2010-10-21", "3", "www.texastribune.org/2012/09/17/farm-table-caucus-advances-local-food-movement/", "2012-09-17", "3", "http://blog.chron.com/kuffsworld/2012/12/the-lege-does-not-need-term-limits/", "2012-12-10", "3", "http://www.statesman.com/news/news/opinion/austin-faces-gathering-storm-over-rates-1/nRpNW/", "2012-06-09", "2", "http://www.statesman.com/news/news/state-regional-govt-politics/capitol-digest-austin-tree-cutting-rules-chopped-h/nRbCp/", "2011-05-20", "2", "http://www.statesman.com/news/news/opinion/communities-of-interest-and-communities-of-confusi/nRZ2W/", "2011-05-13", "2", "http://www.statesman.com/news/news/local/hasan-to-be-transferred-to-bell-co-jail-details-re/nRrSk/", "2010-03-22", "2", "http://www.statesman.com/news/news/state-regional-govt-politics/lawmakers-seek-to-help-the-disabled-get-state-cont/nRRPL/", "2009-11-13", "2", "www.texastribune.org/2015/05/14/end-road-tesla-uber-bills/", "2015-05-14", "2", "www.texastribune.org/2009/02/02/waiting/", "2009-02-02", "2", "www.texastribune.org/2008/04/14/how-it-all-came-out/", "2008-04-14", "2", "www.texastribune.org/2006/06/04/general-election-the-house/", "2006-06-04", "2", "www.texastribune.org/2003/02/03/key-change-from-minor-to-major/", "2003-02-03", "2", "www.texastribune.org/2015/05/06/bill-limit-protest-could-prompt-epa-review/", "2015-05-06", "2", "http://www.statesman.com/news/news/state-regional-govt-politics/special-session-puts-kink-in-lawmakers-plans/nRRZp/", "2009-11-13", "2", "http://www.chron.com//news/politics/article/Uncontested-candidates-in-Texas-races-1475246.php", "2004-11-03", "2", "http://www.nytimes.com/2012/12/21/us/arming-more-texans-to-fight-gun-violence.html", "2012-12-21", "1", "http://www.statesman.com/news/news/state-regional-govt-politics/environmental-bills-make-rounds-at-legislature/nWs6N/", "2013-03-15", "1", "http://www.austin360.com/news/entertainment/dining/east-side-king-to-open-brick-and-mortar-on-dec-4-t/nTGCt/", "2012-11-28", "1", "http://www.statesman.com/news/news/opinion/keep-eye-on-eb-5-green-jobs-program/nRmX4/", "2012-03-28", "1", "http://www.statesman.com/news/business/mayor-proposes-green-jobs-investment-program-for-a/nRmWX/", "2012-03-26", "1", "http://www.statesman.com/news/news/local-education/austin-district-to-take-up-charter-school-issue-to/nRh8X/", "2011-12-18", "1", "http://www.statesman.com/news/news/local/developer-pledges-25000-to-effort-to-help-east-aus/nRdkq/", "2011-08-22", "1", "http://www.statesman.com/news/news/state-regional-govt-politics/capitol-digest-senate-backs-tougher-human-traffick/nRYZk/", "2011-03-23", "1", "http://www.statesman.com/news/news/local/urban-affairs-electric-rates-to-increase-10-12-per/nRX2g/", "2011-03-02", "1", "http://www.statesman.com/news/news/state-regional-govt-politics/legislative-odd-couple-teaming-up-on-payday-lendin/nRW7T/", "2011-01-27", "1", "http://www.statesman.com/news/news/state-regional-govt-politics/how-central-texas-lawmakers-spent-campaign-donatio/nRRbL/", "2009-11-13", "1", "http://www.statesman.com/news/business/chinese-investors-checking-out-texas-austin/nXnw2/", "2013-05-10", "1", "http://www.dallasnews.com/news/politics/headlines/20130224-looking-to-add-dried-fruits-to-your-breakfast-toast-and-jam.ece", "2013-02-23", "1", "www.texastribune.org/2013/04/23/teslas-efforts-texas-trouble/", "2013-04-23", "1", "www.texastribune.org/2011/02/24/colin-goddard-bears-witness-to-campus-massacre-/", "2011-02-24", "1", "www.texastribune.org/2010/12/13/fat-and-skinny/", "2010-12-13", "1", "www.texastribune.org/2009/06/15/something-special/", "2009-06-15", "1", "www.texastribune.org/2009/01/12/gloomy-but-still-in-the-black/", "2009-01-12", "1", "www.texastribune.org/2005/01/17/easy-as-pie/", "2005-01-17", "1", "www.texastribune.org/2002/08/12/a-call-for-a-political-cease-fire/", "2002-08-12", "1", "www.texastribune.org/2002/04/01/switch-hitters/", "2002-04-01", "1", "http://www.chron.com//opinion/outlook/article/Bell-Make-room-at-table-for-voters-1929689.php", "2005-04-10", "1", "http://www.chron.com//news/houston-texas/article/Perry-signs-bill-allowing-guns-inside-City-Hall-2125145.php", "2003-06-21", "1", "http://www.chron.com//news/texas/article/Leaders-Agreement-on-80-6-B-Texas-budget-reached-1389437.php", "2011-05-20", "1", "http://www.texasobserver.org/2940-political-intelligence-criminal-injustice/", "2009-01-23", "1", "http://www.statesman.com/news/news/state-regional-govt-politics/as-court-fight-looms-over-voter-id-those-who-hav-1/nRp2f/", "2012-07-07", "1", "http://www.statesman.com/news/news/state-regional-govt-politics/senate-takes-different-path-from-house-on-environm/nRZ2p/", "2011-05-13", "1", "www.texastribune.org/2013/05/22/days-left-negotiate-key-details-education-bills/", "2013-05-22", "1", "http://www.chron.com//news/houston-texas/article/Texas-embraces-amendment-on-gay-marriage-1519660.php", "2004-02-25", "1", "http://www.chron.com//news/article/House-OKs-daily-pledge-in-schools-2104240.php", "2003-05-07", "1", "www.texastribune.org/2010/03/11/the-brief-top-texas-news-for-mar-11-2010/", "2010-03-11", "1", "www.texastribune.org/2011/02/22/wentworth-rodriguez-debate-campus-carry-on-cnn/", "2011-02-22", "1", "http://www.chron.com//opinion/outlook/article/Hines-Take-breath-before-remapping-mayhem-1563304.php", "2005-03-09", "1", "http://www.dallasnews.com/news/state/headlines/20110217-parties-find-common-ground-on-animal-rights-legislation.ece", "2011-02-16", "1", "http://www.statesman.com/news/news/opinion/cooper-lewis-child-nutrition-starts-first-thing-in/nXQNf/", "2013-04-21", "1", "http://www.statesman.com/news/news/local/ten-years-later-homestead-preservation-districts-s/njwhQ/", "2015-01-24", "1", "http://trailblazersblog.dallasnews.com/2013/05/bills-aim-to-help-schools-make-kids-healthy.html/", "2013-05-07", "1")

runTopicModelingOnCommunity(tsvfile,k,highend,lowend,path_to_tsvs,articlesForCommunity,debug=T)




'''with high 5000 and low 1000
Topic 16        13.39   foundation        error       bounds    subscript    xchildren     marriage   efficiency      courses         stem          tsa
Topic 2         9.48          war   resolution     policies     overseas     defeated      silence       minors       bypass   ayotzinapa     guerrero
Topic 7         8.65   foundation        solar       models    renewable          aug   incentives    sanctuary          epa    moncrease       denton
Topic 15         7.81    seniority         seth     patients distributors      renters        craft     articles          feb      metzger      brewers
Topic 3         6.42     defeated   nomination          win       straus      fitness     expenses        hutto kleinschmidt    detainees          aei
'''

saveArticleTexts <- function(tsvfile,path_to_tsvs,debug=FALSE){
  SEED <- 2010   #for reproducibility 
  pol_tsvfile = paste(path_to_tsvs,tsvfile,sep="")
  eddr <- suppressWarnings( read.delim(file=pol_tsvfile,header = T, sep="\t") )
  ps <- strsplit(pol_tsvfile,"/")
  entitynamefull <- ps[[1]][length(ps[[1]])]
  entityname <- strsplit(entitynamefull,"-articles.tsv")[[1]][1]
  if( nrow(eddr) > 0){
    print(entitynamefull)
    fileout <- paste(path_to_tsvs,entityname,"-articletexts.txt",sep="")
    write(paste(eddr[,'text'], collapse = ''),file=fileout,append=F)  
  }
}

saveArticleTextsAfterCutoff <- function(tsvfile,path_to_tsvs,debug=FALSE){
  SEED <- 2010   #for reproducibility 
  pol_tsvfile = paste(path_to_tsvs,tsvfile,sep="")
  eddr <- suppressWarnings( read.delim(file=pol_tsvfile,header = T, sep="\t") )
  ps <- strsplit(pol_tsvfile,"/")
  entitynamefull <- ps[[1]][length(ps[[1]])]
  entityname <- strsplit(entitynamefull,"-articles.tsv")[[1]][1]
  if( nrow(eddr) > 0){
      JSS_papers <- eddr
      corpus <- Corpus(VectorSource(sapply(JSS_papers[, "text"], remove_HTML_markup)))            
      JSS_dtm <- DocumentTermMatrix(corpus, control = list(stopwords = TRUE, minWordLength = 3, removeNumbers = TRUE, removePunctuation = TRUE))
      term_tfidf <- tapply( JSS_dtm$v/row_sums(JSS_dtm)[JSS_dtm$i], JSS_dtm$j, mean) * log2( nDocs(JSS_dtm) / col_sums(JSS_dtm > 0))
      number_of_initial_terms <- length(term_tfidf)
      
      cutoffvals <- get_cutoffval_and_type(term_tfidf,highend,lowend)
      cutoff <- cutoffvals$cutoff
      cutoff_type <- cutoffvals$cutoff_type                           
      JSS_dtm <- JSS_dtm[,term_tfidf >= cutoff]   #only include those that have tfidf of at least cutoff value
      JSS_dtm <- JSS_dtm[row_sums(JSS_dtm) > 0,]  #this removes empty documents ( ie, no terms found in them so sum of terms if zero)
      #post_cutoff_terms <- ncol(JSS_dtm)
      post_cutoff_terms <- colnames(JSS_dtm)
      #print(post_cutoff_terms)
      print(entitynamefull)
      fileout <- paste(path_to_tsvs,"aftercutoff/",entityname,"-articletexts-after-tfidf-cutoff.txt",sep="")
      #write(paste(post_cutoff_terms, collapse = ''),file=fileout,append=F)  
      write(paste(post_cutoff_terms, collapse = " "),file=fileout,append=F)  
  }
}

tsvfiles = dir(path_to_tsvs,pattern =".tsv")
for(tsvfile in tsvfiles){
  saveArticleTextsAfterCutoff(tsvfile,path_to_tsvs)
}

#saveArticleTextsAfterCutoff("bob_libal-articles.tsv",path_to_tsvs)






#TOPIC MODELLING ON COMMUNITIES


k <- 20    #number of topics
highend = 4000  #want less than this many terms
lowend = 2000   #want 
tsvfile = "eddie_rodriguez-articles.tsv"
path_to_tsvs = "/Users/dolano/htdocs/dama-larca/d3/generate_network/data/tsvs/"
articlesForCommunity <- read.csv("/Users/dolano/htdocs/dama-larca/d3/whoyouelect-april27/lda/community-articles-lda.csv",header = F, stringsAsFactors=FALSE)
colnames(articlesForCommunity) <- c("url","date","entities")

#single words, above 0
ngramtype <- 1
runTopicModelingOnCommunity(tsvfile,k,highend,lowend,path_to_tsvs,articlesForCommunity,ngramtype,above=0,weighbyentity = F, debug=T)

#bi-grams, above 0
ngramtype <- 2
runTopicModelingOnCommunity(tsvfile,k,highend,lowend,path_to_tsvs,articlesForCommunity,ngramtype,above=0,weighbyentity = F,debug=T)

#single words , above 1
ngramtype <- 1
runTopicModelingOnCommunity(tsvfile,k,highend,lowend,path_to_tsvs,articlesForCommunity,ngramtype,above=1,weighbyentity = F,debug=T)

#bi-grams words , above 1
ngramtype <- 2
runTopicModelingOnCommunity(tsvfile,k,highend,lowend,path_to_tsvs,articlesForCommunity,ngramtype,above=1,weighbyentity = F,debug=T)

#single words , above 2
ngramtype <- 1
runTopicModelingOnCommunity(tsvfile,k,highend,lowend,path_to_tsvs,articlesForCommunity,ngramtype,above=2,weighbyentity = F,debug=T)

#bi-grams words , above 1
ngramtype <- 2
runTopicModelingOnCommunity(tsvfile,k,highend,lowend,path_to_tsvs,articlesForCommunity,ngramtype,above=2,weighbyentity = F,debug=T)

#single words , above 3
ngramtype <- 1
runTopicModelingOnCommunity(tsvfile,k,highend,lowend,path_to_tsvs,articlesForCommunity,ngramtype,above=3,weighbyentity = F,debug=T)

#bi-grams words , above 3
ngramtype <- 2
runTopicModelingOnCommunity(tsvfile,k,highend,lowend,path_to_tsvs,articlesForCommunity,ngramtype,above=3,weighbyentity = F,debug=T)


#what if i try weighing by the number of entities each one has ( just copy text entity number of times and put in as new text)
#include weights by entity and exclude 1, single words
#k = 20
#k = 10   # <--- this is better than 20 definitely
k = 5
ngramtype <- 1
weighbyentity = T  
runTopicModelingOnCommunity(tsvfile,k,highend,lowend,path_to_tsvs,articlesForCommunity,ngramtype,above=1,weighbyentity = T,debug=T)

k = 5
ngramtype <- 2
weighbyentity = T  
runTopicModelingOnCommunity(tsvfile,k,highend,lowend,path_to_tsvs,articlesForCommunity,ngramtype,above=1,weighbyentity = T,debug=T)




#include weights by entity and exclude 1, bi-grams
k = 20
ngramtype <- 2
weighbyentity = T  
runTopicModelingOnCommunity(tsvfile,k,highend,lowend,path_to_tsvs,articlesForCommunity,ngramtype,above=1,weighbyentity = T,debug=T)





#or what if i just search for the number of topics which is equal to the max number of entities.. in this case 6 ( getting rid of noise)
#single words , above 1
k = 6
ngramtype <- 1
runTopicModelingOnCommunity(tsvfile,k,highend,lowend,path_to_tsvs,articlesForCommunity,ngramtype,above=1,weighbyentity = F,debug=T)

#bi-grams words , above 1
k = 6
ngramtype <- 2
runTopicModelingOnCommunity(tsvfile,k,highend,lowend,path_to_tsvs,articlesForCommunity,ngramtype,above=1,weighbyentity = F,debug=T)








runTopicModelingOnCommunity <- function(tsvfile,k,highend,lowend,path_to_tsvs,articlesForCommunity,ngramtype,above,weighbyentity = FALSE,debug=FALSE){
  SEED <- 2010   #for reproducibility 
  #for every tsv in folder
  #pol_tsvfile = "/Users/dolano/htdocs/dama-larca/d3/whoyouelect-april27/lda/eddie_rodriguez-articles.tsv"
  pol_tsvfile = paste(path_to_tsvs,tsvfile,sep="")
  eddr <- suppressWarnings( read.delim(file=pol_tsvfile,header = T, sep="\t", stringsAsFactors=FALSE) )
  ps <- strsplit(pol_tsvfile,"/")
  entitynamefull <- ps[[1]][length(ps[[1]])]
  entityname <- strsplit(entitynamefull,"-articles.tsv")[[1]][1]
  
  #dim(eddr)  #780 articles with 6 fields each
  if( nrow(eddr) > 0){ 
    
    #now only keep urls from eddr that are in articlesForCommunity
    articleurls <- articlesForCommunity[,1]
    artscount <- 0
    neweddr <- as.data.frame(matrix(nrow=60,ncol=6))
    colnames(neweddr) <- colnames(eddr)
    #[1] "title"    "date"     "source"   "url"      "language" "text"  
    nr <- 1
    for( r in 1:nrow(eddr)){ 
        #print(r)
        if(eddr[r,4] %in% articleurls){    
             aid <- which(articleurls == eddr[r,4])
             entitynumforarticle <- articlesForCommunity[aid,3]
             if(entitynumforarticle > above){
                 artscount <- artscount + 1
                 neweddr[nr,1] <- paste(eddr[r,1])     #title
                 neweddr[nr,2] <- paste(eddr[r,2])     #date
                 neweddr[nr,3] <- paste(eddr[r,3])     #source
                 neweddr[nr,4] <- paste(eddr[r,4])     #url
                 neweddr[nr,5] <- paste(eddr[r,5])     #language
                 if(weighbyentity == FALSE){
                    neweddr[nr,6] <- paste(eddr[r,6])     #text
                 }else{
                   #add more of the same row ( and update nr according )
                    neweddr[nr,6] <- paste(eddr[r,6]) #complete current row 
                    #neweddr <- neweddr[rep(eddr, entitynumforarticle - 1), 1:6]
                    for(t in 1:(entitynumforarticle - 1)){
                        #neweddr <- rbind(rep(eddr[r,1:6], entitynumforarticle - 1), neweddr)
                        neweddr <- rbind(eddr[r,1:6], neweddr)
                    }
                    nr <- nr +  entitynumforarticle - 1
                 }
                 nr <- nr + 1
             }
        }
    }
    #colnames(neweddr) <- colnames(eddr)
    #print(dim(neweddr))
    #return(0)
  
    #JSS_papers <- eddr
    JSS_papers <- neweddr
    corpus <- Corpus(VectorSource(sapply(JSS_papers[, "text"], remove_HTML_markup)))              
    if(ngramtype == 1){
      JSS_dtm <- DocumentTermMatrix(corpus, control = list(stopwords = TRUE, minWordLength = 3, removeNumbers = TRUE, removePunctuation = TRUE))  
    }else{
      BigramTokenizer <- function(x) unlist(lapply(ngrams(words(x), 2), paste, collapse = " "), use.names = FALSE)
      JSS_dtm <- DocumentTermMatrix(corpus, control = list(stopwords = TRUE, minWordLength = 3, removeNumbers = TRUE, removePunctuation = TRUE, tokenize = BigramTokenizer)) 
    }
    term_tfidf <- tapply( JSS_dtm$v/row_sums(JSS_dtm)[JSS_dtm$i], JSS_dtm$j, mean) * log2( nDocs(JSS_dtm) / col_sums(JSS_dtm > 0))
    number_of_initial_terms <- length(term_tfidf)
    
    cutoffvals <- get_cutoffval_and_type(term_tfidf,highend,lowend)
    cutoff <- cutoffvals$cutoff
    cutoff_type <- cutoffvals$cutoff_type                           
    JSS_dtm <- JSS_dtm[,term_tfidf >= cutoff]   #only include those that have tfidf of at least cutoff value
    JSS_dtm <- JSS_dtm[row_sums(JSS_dtm) > 0,]  #this removes empty documents ( ie, no terms found in them so sum of terms if zero)
    post_cutoff_terms <- ncol(JSS_dtm)
  
    jss_TM <- list( VEM       = LDA(JSS_dtm, k = k, control = list(seed = SEED)))   #run Latent Dirichlet Allocation with values
    Topic <- topics(jss_TM[["VEM"]], 1)   #contains the most likely topic for each document.. length(Topic) is number of documents, k is number of topics
    Topic <- as.factor(Topic)
    Terms <- terms(jss_TM[["VEM"]], 10)   #top 10 most frequent terms for each topic are obtained, row is Topic, columns are terms
    
    #FUTURE IMPROVEMENTS
    #posterior(jss_TM[["VEM"]])
    #
    
    if(debug == TRUE){
      #print(Terms[1:10,1:20])  #shows top 10 terms for 20 topics
      print(Terms)
      print(sort(summary(as.factor(Topic)))) #to see spread of how many documents are associated with each topic
    }
    
    #HOW TO FIND ARTICLES ASSOCIATED WITH A TOPIC
    #which(Topic == 19)   #gives ids for documents associated with topic 19, then use eddr[which(Topic == 19),5] to get articles .. i think
    
    summary_topic <- summary(as.factor(Topic)) 
    most_frequent_topics <- as.numeric(names(sort(summary_topic,decreasing=TRUE)))
    most_frequent_topics_documents <- sapply(most_frequent_topics,function(a){ summary_topic[a][[1]]})  
    most_frequent_percents <- sapply(most_frequent_topics_documents,function(a){ round(100 * a / sum(summary_topic),2)})
    importanttopics <- terms(jss_TM[["VEM"]], 10)[,most_frequent_topics]
    importanttopics_withpercentaages <- rbind(most_frequent_percents,importanttopics)
    
    line <- paste(entityname,nrow(eddr),number_of_initial_terms, cutoff, cutoff_type, nrow(JSS_dtm),post_cutoff_terms )  
    print(line)
    write.table(format(t(importanttopics_withpercentaages), justify="left"), row.names=TRUE, col.names=F, quote=F,sep=",")
    #fileout <- paste(path_to_tsvs,"SUMMARIZINGpoliticians-3grams.out",sep="")
    #write(line,file=fileout,append=TRUE)  
    #write.table(format(t(importanttopics_withpercentaages), justify="left"), file=fileout, append=TRUE,row.names=TRUE, col.names=F, quote=F,sep=",")
  }else{
    print(paste(entityname,"has no articles so don't include"))
  }
}

cc <- rep(0,times=nrow(posterior(jss_TM[["VEM"]])$topics))
for(i in 1:nrow(posterior(jss_TM[["VEM"]])$topics)){ 
  cc[i] <- sort(posterior(jss_TM[["VEM"]])$topics[i,])[5] - sort(posterior(jss_TM[["VEM"]])$topics[i,])[4] 
}
