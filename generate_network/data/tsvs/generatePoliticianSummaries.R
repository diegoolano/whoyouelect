library("topicmodels")
library("tm")
library("XML")
library("slam")

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
  JSS_dtm <- DocumentTermMatrix(corpus, control = list(stopwords = TRUE, minWordLength = 3, removeNumbers = TRUE, removePunctuation = TRUE))
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
  
  summary_topic <- summary(as.factor(Topic))
  #most_frequent_topic <- which.max(summary_topic)[[1]]  
  #second_most_frequent_topic <- as.numeric(names(sort(summary_topic,decreasing=TRUE))[2])
  #third_most_frequent_topic  <-  as.numeric(names(sort(summary_topic,decreasing=TRUE))[3])
  #fourth_most_frequent_topic  <-  as.numeric(names(sort(summary_topic,decreasing=TRUE))[4])
  #fifth_most_frequent_topic  <-  as.numeric(names(sort(summary_topic,decreasing=TRUE))[5])
  
  most_frequent_topics <- as.numeric(names(sort(summary_topic,decreasing=TRUE)))
 
  #most_frequent_topic_documents <- summary_topic[most_frequent_topic][[1]]
  #second_most_frequent_topic_documents <- summary_topic[second_most_frequent_topic][[1]]
  #third_most_frequent_topic_documents <- summary_topic[third_most_frequent_topic][[1]]
  #fourth_most_frequent_topic_documents <- summary_topic[fourth_most_frequent_topic][[1]]
  #fifth_most_frequent_topic_documents <- summary_topic[fifth_most_frequent_topic][[1]]
  
  most_frequent_topics_documents <- sapply(most_frequent_topics,function(a){ summary_topic[a][[1]]})
  
  #mf_percent <- round(100 * most_frequent_topic_documents / sum(summary_topic),2)
  #sf_percent <- round(100 * second_most_frequent_topic_documents / sum(summary_topic),2)
  #tf_percent <- round(100 * third_most_frequent_topic_documents / sum(summary_topic),2)
  #fof_percent <- round(100 * fourth_most_frequent_topic_documents / sum(summary_topic),2)
  #fif_percent <- round(100 * fifth_most_frequent_topic_documents / sum(summary_topic),2)
  
  most_frequent_percents <- sapply(most_frequent_topics_documents,function(a){ round(100 * a / sum(summary_topic),2)})
  
  #importanttopics <- terms(jss_TM[["VEM"]], 10)[, c(most_frequent_topic,second_most_frequent_topic,third_most_frequent_topic,fourth_most_frequent_topic,fifth_most_frequent_topic)]
  #importanttopics_withpercentaages <- rbind(c(mf_percent,sf_percent,tf_percent,fof_percent,fif_percent),importanttopics)
  
  importanttopics <- terms(jss_TM[["VEM"]], 10)[,most_frequent_topics]
  importanttopics_withpercentaages <- rbind(most_frequent_percents,importanttopics)
  
  #print(paste(entityname,nrow(eddr),number_of_initial_terms, cutoff, cutoff_type, nrow(JSS_dtm),post_cutoff_terms ))
  #print.matrix(t(importanttopics_withpercentaages))
  line <- paste(entityname,nrow(eddr),number_of_initial_terms, cutoff, cutoff_type, nrow(JSS_dtm),post_cutoff_terms )  
  print(line)
  fileout <- paste(path_to_tsvs,"SUMMARIZINGpoliticians.out",sep="")
  write(line,file=fileout,append=TRUE)  
  write.table(format(t(importanttopics_withpercentaages), justify="left"), file=fileout, append=TRUE,row.names=TRUE, col.names=F, quote=F,sep=",")
  }else{
    print(paste(entityname,"has no articles so don't include"))
  }
}



##START HERE
path_to_tsvs = "/Users/dolano/htdocs/dama-larca/d3/generate_network/data/tsvs/"
##tsvfiles = dir(path_to_tsvs,pattern =".tsv")

#parameters to set
k <- 20    #number of topics
highend = 4000  #want less than this many terms
lowend = 2000   #want more than this many terms
#cutoff <- 0.04   #<-- this is set automatically based on the highend lowend terms

#to fix fuck ups "allen_fletcher-articles-fixed.tsv",
tsvfiles = c("ana_hernandez-articles-fixed.tsv","borris_miles-articles-fixed.tsv")

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

#tsvfile = "eddie_rodriguez-articles.tsv"

runTopicModelingOn(tsvfile,k,highend,lowend,path_to_tsvs,debug=T)



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


