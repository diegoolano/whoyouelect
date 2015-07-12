from dama_globals import *
from dama_utils import *
import time
import sys
import copy
import traceback


def handle_single_match_same_sentence(sentn, relations, ent_to_global,same_sent,global_index_val, loc_index,sentences, debug):
    if debug:
            printflush("In Handle Single Match Same Sentence with Sent num: "+str(sentn))
    
    #TODO MAKE THIS WORK FOR OTHER ENTITIES (right now its the politician you are searching for centeric) 
    for i, s in enumerate(same_sent):
        if debug:                
            printflush("Same sentence item:")
            printflush(s)

        if s['name'] == loc_index:                
            if debug:
                printflush("found itself so don't add relation")
            continue                    
        else:                                
            t2id = ent_to_global[s['name']]

            #MAKE SURE THE TWO TERMS ARE NOT THE SAME (use ids and maybe substring)
            if global_index_val == t2id:
                    if debug:
                        printflush("DO NOT ADD AS THEY ARE THE SAME ENTITY GLOBABLY")
            else:                    
                #MAKE SURE RELATION NOT ALREADY IN
                exists = 0
                for rela in relations:
                    if rela['term1_id'] == global_index_val and rela['term2_id'] == t2id and rela['type'] == "same sentence" and rela['sentence_num'] == sentn:
                        exists = 1

                if exists == 0:   
                    if debug:
                        printflush("\tadd SAME SENTENCE relationship between "+loc_index +" (id: "+str(global_index_val)+") and "+s['name']+" (id: "+str(t2id)+") at sentence: "+str(sentn))
                    relations.append({'term1':loc_index, 'term1_id':global_index_val, 
                                      'term2':s['name'], 'term2_id':t2id, 'type':'same sentence', 
                                      'text_snippet':sentences[sentn], 'sentence_num':sentn})
                else:
                    if debug:
                        printflush("\tRELATION ARLEADY EXISTS LOCALLY SO DON'T ADD IT")

        #TODO CHECK IF these relations are in global_relations, though if you base things with url as key, you should be ok
        #AT END YOU'LL JUST HAVE TO POST PROCESS the global_relations list to get a list that is based on (t1id,t2id) keys  
        
    return relations

def handle_single_match_near_sentences(sentn,subtype,ent_to_global, near_sents, global_index_val, loc_index, relations, sentences,debug):
    if debug:
        printflush("in handle_single_match_near_sentences with "+subtype+", "+str(near_sents))
    for i,se in enumerate(near_sents):
        if debug:            
            printflush(se)
        for s in se:
            if s['name'] != loc_index:
                
                if subtype =='prior':
                    thissent = sentn - number_sentences_for_context + i
                    dist = number_sentences_for_context - i
                    if thissent < 0:
                        thissent = 0 + i
                        dist = sentn - thissent
                else:
                    thissent = sentn + i + 1
                    dist = i + 1

                t2id = ent_to_global[s['name']]
                if global_index_val == t2id:
                    if debug:
                        printflush("DO NOT ADD AS THEY ARE THE SAME ENTITY GLOBABLY")
                else:

                    #MAKE SURE RELATION NOT ALREADY IN
                    exists = 0
                    for rela in relations:
                        if rela['term1_id'] == global_index_val and rela['term2_id'] == t2id and rela['type'] == "near":
                            if rela['subtype'] == subtype:
                                if rela['subtype'] == 'prior' and rela['sentence_num'] == [thissent,sentn]:
                                    exists = 1                                
                                if rela['subtype'] == 'post' and rela['sentence_num'] == [sentn,thissent]:
                                    exists = 1                                

                    if exists == 0: 
                        if subtype == 'prior':
                            if debug:
                                printflush("\nadd PRIOR relationship between "+loc_index +" and "+s['name'])

                            relations.append({'term1':loc_index, 'term1_id':global_index_val, 
                                              'term2':s['name'], 'term2_id':t2id, 'type':'near', 'subtype':subtype, 'distance': str(dist), 
                                              'text_snippet':" ".join(sentences[thissent:sentn+1]), 'sentence_num':[thissent,sentn]})
                        else:
                            if debug:
                                printflush("\nadd NEXT relationship between "+loc_index +" and "+s['name'])
                                
                            relations.append({'term1':loc_index, 'term1_id':global_index_val, 
                                              'term2':s['name'], 'term2_id':t2id, 'type':'near', 'subtype':subtype, 'distance': str(dist), 
                                              'text_snippet':" ".join(sentences[sentn:thissent+1]), 'sentence_num':[sentn,thissent]})
                            
                    else:
                        if debug:
                            printflush("\tRELATION ARLEADY EXISTS LOCALLY SO DON'T ADD IT")

                #TODO CHECK IF these relations are in global_relations, though if you base things with url as key, you should be ok
                #AT END YOU'LL JUST HAVE TO POST PROCESS the global_relations list to get a list that is based on 
                #(t1id,t2id) keys  
                
    return relations

def handle_single_match_far_sentences(ent_to_global, rest, global_index_val, loc_index, relations, debug):
    if debug:
        printflush("In handle_single_match_far_sentences with rest")
        printflush(rest)
        
    for i,se in enumerate(rest):
        if debug:
            printflush(se)

        for s in se:
            if debug:
                printflush(s)
                
            if s['name'] != loc_index:                
                t2id = ent_to_global[s['name']]
                
                if global_index_val == t2id:
                    if debug:
                        printflush("DO NOT ADD AS THEY ARE THE SAME ENTITY GLOBABLY")
                else:
                    #MAKE SURE RELATION NOT ALREADY IN
                    exists = 0
                    for rela in relations:
                        if rela['term1_id'] == global_index_val and rela['term2_id'] == t2id and rela['type'] == "same article":                            
                            exists = 1    

                    if exists == 0:                              
                        if debug:
                            printflush("\nadd FAR relationship between "+loc_index +" and "+s['name'])

                        relations.append({'term1':loc_index, 'term1_id':global_index_val, 
                                          'term2':s['name'], 'term2_id':t2id, 'type':'same article'})
                    else:
                        if debug:
                            printflush("\tRELATION ARLEADY EXISTS LOCALLY SO DON'T ADD IT" )
    return relations



def handle_multiple_match_near_sentences(sentnums,bgrelations,ent_to_global,global_index_val,loc_index,relations,sentences, debug):        
    if debug:
        printflush("Function: In Handle Multiple Match Near Sentences")
        
    subtype = "prior"
    priorn = 0
    priornext_sents = []
    for i,sentn in enumerate(sentnums):
        same_sent, prior_sents, next_sents, prior_far_sents, next_far_sents = bgrelations[i]  
        if debug:
            printflush("\t sentnum: "+str(sentn)+" with prior sents!")
            printflush(prior_sents )

        if priorn == 0:
            if debug:
                printflush("First one so no overlap")
            relations = handle_single_match_near_sentences(sentn,subtype,ent_to_global, prior_sents, global_index_val, loc_index, relations, sentences, debug)                                 
            priorn = sentn
            priornext_sents= next_sents
        else:
            if debug:
                printflush("Not first match so look for overlaps with prior")

            diff = sentn - priorn
            if diff > 2 * number_sentences_for_context:
                if debug:
                    printflush("Diff between current "+str(sentn)+" and prior "+str(priorn)+ " is greater than 2xcontext so you're good")
                relations = handle_single_match_near_sentences(sentn,subtype,ent_to_global, prior_sents, global_index_val, loc_index, relations, sentences, debug)                                 
                priorn = sentn
                priornext_sents= next_sents
            else:
                #there may be some overlap between this prior_sents and the priornext_sents
                if debug:
                    printflush("Dist less than 2xcontent so checking for overlap between prior "+ str(priorn) +" nexts")
                    printflush(priornext_sents)
                    printflush("and current "+str(sentn)+" priors")
                    printflush(prior_sents)

                #make sure all prior sents are closest to current sentn and not others in sentnums!
                #this implementation assumes 3 sentence diameter!!
                priornext_len = 3
                
                if len(priornext_sents) != 3:
                    if debug:
                        printflush("*(*(*(*(*ERROR: Prior Next Sent less than three.  TODO FIX")
                        printflush(priornext_sents)
                else:
                    if priornext_sents[2] == []:
                        priornext_len = priornext_len -1
                        if priornext_sents[1] == []:
                            priornext_len = priornext_len - 1
                            if priornext_sents[0] == []:
                                priornext_len = priornext_len - 1                                
                #so priornext_len shows who far the prior next_sents goes till
                
                curprior_len = 3
                if len(prior_sents) != 3:
                    if debug:
                        printflush("_)_)_)_)_)_)_)ERROR: Prior Sent less than three.  TODO FIX")
                        printflush(prior_sents)
                else:    
                    if prior_sents[0] == []:
                        curprior_len = curprior_len -1
                        if prior_sents[1] == []:
                            curprior_len = curprior_len -1
                            if prior_sents[0] == []:
                                curprior_len = curprior_len - 1                                
                #curprior_len holds how far back current prior goes

                if priorn + priornext_len < sentn - curprior_len:
                    if debug:
                        printflush("NO overlap between prior's farthest right sentence at "+str(priorn + priornext_len))
                        printflush("and current left most prior at "+str(sentn - curprior_len))
                    relations = handle_single_match_near_sentences(sentn,subtype,ent_to_global, prior_sents, global_index_val, loc_index, relations, sentences, debug)                                 
                    priorn = sentn
                    priornext_sents= next_sents
                else:
                    #there is a conflict!
                    if diff == 1:
                        if debug:
                            printflush("Matches are one string away from one another so remove both prior next  and current prior")
                        bgrelations[i-1][2] = []
                        bgrelations[i][1] = []
                    if diff == 2:
                        if debug:
                            printflush("Matches are two strings away from one another so remove prior next  and keep only current prior one back")
                        bgrelations[i-1][2] = []
                        bgrelations[i][1] = [bgrelations[i][1][2]]
                    if diff == 3:
                        if debug:
                            printflush("Matches are three strings away from one another so keep prior next farthest and keep only current prior one back")
                        bgrelations[i-1][2] = [bgrelations[i-1][2][2]]
                        bgrelations[i][1] = [bgrelations[i][1][2]]
                    if diff == 4:
                        if debug:
                            printflush("Matches are four strings away from one another so keep prior next farthest and keep current prior two back")
                        bgrelations[i-1][2] = [bgrelations[i-1][2][2]]
                        bgrelations[i][1] = [bgrelations[i][1][1],bgrelations[i][1][2]]                        
                    if diff == 5:
                        if debug:
                            printflush("Matches are five strings away from one another so keep prior next farthest two and keep current prior two back")
                        bgrelations[i-1][2] = [bgrelations[i-1][2][1],bgrelations[i-1][2][2]]
                        bgrelations[i][1] = [bgrelations[i][1][1],bgrelations[i][1][2]]                        
                    if diff == 6:
                        if debug:
                            printflush("Matches are six strings away from one another so keep prior next farthest two and keep current prior")
                        bgrelations[i-1][2] = [bgrelations[i-1][2][1],bgrelations[i-1][2][2]]

                    prior_sents = bgrelations[i][1]
                    relations = handle_single_match_near_sentences(sentn,subtype,ent_to_global, prior_sents, global_index_val, loc_index, relations, sentences, debug)                                 
                    priorn = sentn
                    priornext_sents= next_sents

    return [relations,bgrelations]
                        
    
def handle_multiple_match_far_sentences(sentnums,bgrelations,sentences,ent_to_global,global_index_val,loc_index,relations,dis_entities,debug):        
    if debug:
        printflush("Function: Handle Multiple Match Far Sentence")
        
    tot = len(sentnums)
    same_sent, prior_sents, next_sents, prior_far_sents, next_far_sents = bgrelations[0]
    i = 0
    rang = []
    keep = []
    if sentnums[i] >= 3:
        keep = range(0,sentnums[i]-3)

    while i+1 < len(sentnums):
        if (sentnums[i+1] - sentnums[i]) > 2 * number_sentences_for_context + 1:
            keep = keep + range(sentnums[i]+4,sentnums[i+1]-3)
        i = i + 1

    if debug:
        printflush("Len(sentences): "+str(len(sentences)))
        printflush("i: "+str(i))

    if sentnums[i] + 3 < len(sentences):
        keep = keep + range(sentnums[i] + 4,len(sentences))

    #How to remove non keep indices
    rest = prior_far_sents + next_far_sents        
    if debug:
        printflush("So keep entities from sentences: ")
        printflush(keep)
        printflush("\nRest")
        printflush(rest)
        printflush("\nlen(rest): "+str(len(rest))+"\nDis_Ent")
        printflush(dis_entities)
        printflush("\nSentences")
        printflush(sentences)
        
    keep_res = []
    for i,re in enumerate(rest):
        for ir,r in enumerate(re):
            ee = dis_entities[r['type']][r['name']]
            si = ee["id"].index(r['ent_id'])
            pos_sent = ee["sentence"][si]
            if pos_sent in keep:
                keep_res.append(r)
    if debug:
        printflush("At End Keep res:")
        printflush(keep_res)

    if keep_res != []:
        keep_res = [keep_res]
        relations = handle_single_match_far_sentences(ent_to_global, keep_res, global_index_val, loc_index, relations, debug)                                                   

    return [relations,bgrelations]



def handle_same_extra_single(same_sentence_objs,relations,sentences,debug):
    if debug:
        printflush("FUNCTION: In Handle Same Extra Single")
        
    c = 0
    while c < len(same_sentence_objs) - 1:
        sobj = same_sentence_objs[c]
        sobj_sent = sobj[2]
        i = c + 1
        while i < len(same_sentence_objs):
            sobj2 = same_sentence_objs[i]
            exists = 0
            if sobj[0] == sobj2[0]:
                if debug:
                    printflush("\tFound Same Entity: "+sobj[1] +" (id: "+str(sobj[0])+") and "+sobj2[1]+" (id: "+str(sobj2[0])+") at sentence: "+str(sobj_sent)+" so don't add!")
            else:
                for rela in relations:
                    if ((rela['term1_id'] == sobj[0] and rela['term2_id'] == sobj2[0]) or (rela['term1_id'] == sobj2[0] and rela['term2_id'] == sobj[0])) and rela['type'] == "same sentence" and rela['sentence_num'] == sobj_sent:
                        exists = 1

                if exists == 0:   
                    if debug:
                        printflush("\tadd SAME SENTENCE relationship between "+sobj[1] +" (id: "+str(sobj[0])+") and "+sobj2[1]+" (id: "+str(sobj2[0])+") at sentence: "+str(sobj_sent) )
                    relations.append({'term1':sobj[1], 'term1_id':sobj[0], 
                                      'term2':sobj2[1], 'term2_id':sobj2[0], 'type':'same sentence', 
                                      'text_snippet':sentences[sobj_sent], 'sentence_num':sobj_sent})
                else:
                    if debug:
                        printflush("\tRELATION ARLEADY EXISTS LOCALLY SO DON'T ADD IT")
            i = i + 1
        c = c + 1
    return relations

def handle_same_near_extra_single(same_sentence_objs,near_objs,relations,sentences,debug):
    if debug:
        printflush("FUNCTION: In Handle Same Near Extra Single")
        printflush("Same Sentence_objs:")
        printflush(same_sentence_objs)
        printflush("Near Objs:")
        printflush(near_objs)
    
    c = 0
    while c < len(same_sentence_objs):
        sobj = same_sentence_objs[c]
        sobj_sent = sobj[2]
        
        i = 0        
        while i < len(near_objs):
            sobj2 = near_objs[i]
            sobj2_sent = sobj2[2]
            if sobj2_sent > sobj_sent:
                subtype = "post"                                
                dist = sobj2_sent - sobj_sent
            else:
                subtype = "prior"                
                dist = sobj_sent - sobj2_sent                 

                
            if sobj[0] == sobj2[0]:
                if debug:
                    printflush("\tFound Same Entity: "+sobj[1] +" (id: "+str(sobj[0])+") and "+sobj2[1]+" (id: "+str(sobj2[0])+") so don't add!")
            else:                            
                exists = 0
                for rela in relations:
                    if ((rela['term1_id'] == sobj[0] and rela['term2_id'] == sobj2[0]) or (rela['term1_id'] == sobj2[0] and rela['term2_id'] == sobj[0])) and rela['type'] == "near":                    
                        if rela['subtype'] == subtype:
                            if rela['subtype'] == 'prior' and rela['sentence_num'] == [sobj2_sent,sobj_sent]:
                                exists = 1                                
                            if rela['subtype'] == 'post' and rela['sentence_num'] == [sobj_sent,sobj2_sent]:
                                exists = 1                                

                if exists == 0: 
                    if subtype == 'prior':
                        if debug:
                            printflush("\n\tadd PRIOR relationship between "+sobj[1] +" (id: "+str(sobj[0])+") and "+sobj2[1] +" (id: "+str(sobj2[0])+") at sentence: "+str([sobj2_sent,sobj_sent]) )

                        relations.append({'term1':sobj[1], 'term1_id':sobj[0], 
                                          'term2':sobj2[1], 'term2_id':sobj2[0], 'type':'near', 'subtype':subtype, 'distance': str(dist), 
                                          'text_snippet':" ".join(sentences[sobj2_sent:sobj_sent+1]), 'sentence_num':[sobj2_sent,sobj_sent]})
                    else:
                        if debug:
                            printflush("\n\tadd NEXT relationship between "+sobj[1] +" (id: "+str(sobj[0])+") and "+sobj2[1] +" (id: "+str(sobj2[0])+") at sentence: "+str([sobj_sent,sobj2_sent]) )

                        relations.append({'term1':sobj[1], 'term1_id':sobj[0], 
                                          'term2':sobj2[1], 'term2_id':sobj2[0], 'type':'near', 'subtype':subtype, 'distance': str(dist), 
                                          'text_snippet':" ".join(sentences[sobj_sent:sobj2_sent+1]), 'sentence_num':[sobj_sent,sobj2_sent]})
                else:
                    if debug:
                        printflush("\tRELATION ARLEADY EXISTS LOCALLY SO DON'T ADD IT")
        
            i = i + 1
        c = c + 1
    return relations


def handle_same_far_extra_single(same_sentence_objs,far_objs,relations,sentences,debug):
    #In handle near near extra single with 
    #[[181, u'Page', 0], [183, u'George Nachtigall', 2], [182, u"Harris County Attorney 's Office", 2], [181, u'Page', 3]]
    if debug:
        printflush("FUNCTION: In Handle Same Far Extra Single with ")
        printflush("\tSame Sentence: " + str(same_sentence_objs))
        printflush("\tFar Sentences: " + str(far_objs))
        printflush("\tAll Sentences: " + str(sentences))
        
    c = 0
    while c < len(same_sentence_objs):
        sobj = same_sentence_objs[c]
        sobj_sent = sobj[2]
        i = 0
        while i < len(far_objs):
            sobj2 = far_objs[i]
            sobj2_sent = sobj2[2]
            exists = 0
            if sobj[0] == sobj2[0]:
                if debug:
                    printflush("\tFound Same Entity: "+sobj[1] +" (id: "+str(sobj[0])+") and "+sobj2[1]+" (id: "+str(sobj2[0])+") at sentence: ["+str(sobj_sent)+", "+str(sobj2_sent)+"] so don't add!")
            else:                
                #NEAR or FAR MATCH
                if sobj2_sent > sobj_sent:
                    subtype = "post"                                
                    dist = sobj2_sent - sobj_sent
                else:
                    subtype = "prior"                
                    dist = sobj_sent - sobj2_sent  

                if dist < 4:
                    #NEAR MATCH, unexpected, the fuck
                    if debug:
                        printflush("ERROR: Unexpectedly Found near relationship between "+sobj[1] +" (id: "+str(sobj[0])+") and "+sobj2[1] +" (id: "+str(sobj2[0])+")")
                else:
                    #FAR MATCH
                    exists = 0
                    for rela in relations:
                        if ((rela['term1_id'] == sobj[0] and rela['term2_id'] == sobj2[0]) or (rela['term1_id'] == sobj2[0] and rela['term2_id'] == sobj[0])) and rela['type'] == "same article":                            
                            exists = 1    

                    if exists == 0:                              
                        if debug:
                            printflush("\n\tadd FAR relationship between "+sobj[1] +" (id: "+str(sobj[0])+") and "+sobj2[1] +" (id: "+str(sobj2[0])+")")

                        relations.append({'term1':sobj[1], 'term1_id':sobj[0], 
                                          'term2':sobj2[1], 'term2_id':sobj2[0], 'type':'same article'})
                    else:
                        if debug:
                            printflush("\tRELATION ARLEADY EXISTS LOCALLY SO DON'T ADD IT" )

                    
            i = i + 1
        c = c + 1
    return relations



def handle_near_near_single(near_objs,relations,sentences,debug):
    #In handle near near extra single with 
    #[[181, u'Page', 0], [183, u'George Nachtigall', 2], [182, u"Harris County Attorney 's Office", 2], [181, u'Page', 3]]
    if debug:
        printflush("FUNCTION: In Handle Near Near Extra single with ")
        printflush(near_objs)
        
    c = 0
    while c < len(near_objs) - 1:
        sobj = near_objs[c]
        sobj_sent = sobj[2]
        i = c + 1
        while i < len(near_objs):
            sobj2 = near_objs[i]
            sobj2_sent = sobj2[2]
            exists = 0
            if sobj[0] == sobj2[0]:
                if debug:
                    printflush("\tFound Same Entity: "+sobj[1] +" (id: "+str(sobj[0])+") and "+sobj2[1]+" (id: "+str(sobj2[0])+") at sentence: ["+str(sobj_sent)+", "+str(sobj2_sent)+"] so don't add!")
            else:
                
                if sobj_sent == sobj2_sent:
                    #SAME SENTENCE MATCH, BECAREFUL BECAUSE WE DON'T KNOW WHO IS TERM1,TERM2 in these cases
                    for rela in relations:
                        if ((rela['term1_id'] == sobj[0] and rela['term2_id'] == sobj2[0]) or (rela['term1_id'] == sobj2[0] and rela['term2_id'] == sobj[0])) and rela['type'] == "same sentence" and rela['sentence_num'] == sobj_sent:
                            exists = 1

                    if exists == 0:   
                        if debug:
                            printflush("\tadd SAME SENTENCE relationship between "+sobj[1] +" (id: "+str(sobj[0])+") and "+sobj2[1]+" (id: "+str(sobj2[0])+") at sentence: "+str(sobj_sent))
                        relations.append({'term1':sobj[1], 'term1_id':sobj[0], 
                                          'term2':sobj2[1], 'term2_id':sobj2[0], 'type':'same sentence', 
                                          'text_snippet':sentences[sobj_sent], 'sentence_num':sobj_sent})
                    else:
                        if debug:
                            printflush("\tRELATION ARLEADY EXISTS LOCALLY SO DON'T ADD IT")
                else:
                    #NEAR or FAR MATCH
                    if sobj2_sent > sobj_sent:
                        subtype = "post"                                
                        dist = sobj2_sent - sobj_sent
                    else:
                        subtype = "prior"                
                        dist = sobj_sent - sobj2_sent  
                        
                    if dist < 4:
                        #NEAR MATCH
                        exists = 0
                        for rela in relations:
                            if ((rela['term1_id'] == sobj[0] and rela['term2_id'] == sobj2[0]) or (rela['term1_id'] == sobj2[0] and rela['term2_id'] == sobj[0])) and rela['type'] == "near":                    
                                #We don't car what is the type actually, since either way it will result in double counting
                                #if rela['subtype'] == subtype:
                                #    if rela['subtype'] == 'prior' and rela['sentence_num'] == [sobj2_sent,sobj_sent]:
                                #        exists = 1                                
                                #    if rela['subtype'] == 'post' and rela['sentence_num'] == [sobj_sent,sobj2_sent]:
                                #        exists = 1                                
                                exists = 1

                        if exists == 0: 
                            if subtype == 'prior':
                                if debug:
                                    printflush("\nadd PRIOR relationship between "+sobj[1] +" (id: "+str(sobj[0])+") and "+sobj2[1] +" (id: "+str(sobj2[0])+") at sentence: "+str([sobj2_sent,sobj_sent]) )

                                relations.append({'term1':sobj[1], 'term1_id':sobj[0], 
                                                  'term2':sobj2[1], 'term2_id':sobj2[0], 'type':'near', 'subtype':subtype, 'distance': str(dist), 
                                                  'text_snippet':" ".join(sentences[sobj2_sent:sobj_sent+1]), 'sentence_num':[sobj2_sent,sobj_sent]})
                            else:
                                if debug:
                                    printflush("\nadd NEXT relationship between "+sobj[1] +" (id: "+str(sobj[0])+") and "+sobj2[1] +" (id: "+str(sobj2[0])+") at sentence: "+str([sobj_sent,sobj2_sent]))

                                relations.append({'term1':sobj[1], 'term1_id':sobj[0], 
                                                  'term2':sobj2[1], 'term2_id':sobj2[0], 'type':'near', 'subtype':subtype, 'distance': str(dist), 
                                                  'text_snippet':" ".join(sentences[sobj_sent:sobj2_sent+1]), 'sentence_num':[sobj_sent,sobj2_sent]})
                        else:
                            if debug:
                                printflush("\tRELATION ARLEADY EXISTS LOCALLY SO DON'T ADD IT")
                    else:
                        #FAR MATCH
                        exists = 0
                        for rela in relations:
                            if ((rela['term1_id'] == sobj[0] and rela['term2_id'] == sobj2[0]) or (rela['term1_id'] == sobj2[0] and rela['term2_id'] == sobj[0])) and rela['type'] == "same article":                            
                                exists = 1    

                        if exists == 0:                              
                            if debug:
                                printflush("\nadd FAR relationship between "+sobj[1] +" (id: "+str(sobj[0])+") and "+sobj2[1] +" (id: "+str(sobj2[0])+")")

                            relations.append({'term1':sobj[1], 'term1_id':sobj[0], 
                                              'term2':sobj2[1], 'term2_id':sobj2[0], 'type':'same article'})
                        else:
                            if debug:
                                printflush("\tRELATION ARLEADY EXISTS LOCALLY SO DON'T ADD IT" )
                    
                    
            i = i + 1
        c = c + 1
    return relations

@timeout(100)
def handle_near_far_single(near_objs,far_objs,relations,sentences,debug):
    if debug:
        printflush("FUNCTION: In Handle Near Far Extra Single with ")
        printflush("Nearobks:")
        printflush(near_objs)
        printflush("Far objs")
        printflush(far_objs)
        
    c = 0
    while c < len(near_objs) - 1:
        sobj = near_objs[c]
        sobj_sent = sobj[2]
        i = 0
        while i < len(far_objs):
            sobj2 = far_objs[i]
            sobj2_sent = sobj2[2]
            exists = 0
            if sobj[0] == sobj2[0]:
                if debug:
                    printflush("Found Same Entity: "+sobj[1] +" (id: "+str(sobj[0])+") and "+sobj2[1]+" (id: "+str(sobj2[0])+") at sentence: ["+str(sobj_sent)+", "+str(sobj2_sent)+"] so don't add!")
            else:
                
                if sobj_sent == sobj2_sent:
                    #SAME SENTENCE MATCH, the fuck ERROR!
                    printflush("Error in HANDLE NEAR FAR:  found exact sentence match unexpectedly: "+sobj[1] +" (id: "+str(sobj[0])+") and "+sobj2[1]+" (id: "+str(sobj2[0])+") at sentence: "+str(sobj_sent))
                else:
                    #NEAR or FAR MATCH
                    if sobj2_sent > sobj_sent:
                        subtype = "post"                                
                        dist = sobj2_sent - sobj_sent
                    else:
                        subtype = "prior"                
                        dist = sobj_sent - sobj2_sent  
                        
                    if dist < 4:
                        #NEAR MATCH
                        exists = 0
                        for rela in relations:
                            if ((rela['term1_id'] == sobj[0] and rela['term2_id'] == sobj2[0]) or (rela['term1_id'] == sobj2[0] and rela['term2_id'] == sobj[0])) and rela['type'] == "near":                                                                           
                                exists = 1

                        if exists == 0: 
                            if subtype == 'prior':
                                if debug:
                                    printflush("\nadd PRIOR relationship between "+sobj[1] +" (id: "+str(sobj[0])+") and "+sobj2[1] +" (id: "+str(sobj2[0])+") at sentence: "+str([sobj2_sent,sobj_sent])  )
                                    
                                relations.append({'term1':sobj[1], 'term1_id':sobj[0], 
                                                  'term2':sobj2[1], 'term2_id':sobj2[0], 'type':'near', 'subtype':subtype, 'distance': str(dist), 
                                                  'text_snippet':" ".join(sentences[sobj2_sent:sobj_sent+1]), 'sentence_num':[sobj2_sent,sobj_sent]})
                            else:
                                if debug:
                                    printflush("\nadd NEXT relationship between "+sobj[1] +" (id: "+str(sobj[0])+") and "+sobj2[1] +" (id: "+str(sobj2[0])+") at sentence: "+str([sobj_sent,sobj2_sent]))

                                relations.append({'term1':sobj[1], 'term1_id':sobj[0], 
                                                  'term2':sobj2[1], 'term2_id':sobj2[0], 'type':'near', 'subtype':subtype, 'distance': str(dist), 
                                                  'text_snippet':" ".join(sentences[sobj_sent:sobj2_sent+1]), 'sentence_num':[sobj_sent,sobj2_sent]})
                        else:
                            if debug:
                                printflush("\tRELATION ARLEADY EXISTS LOCALLY SO DON'T ADD IT")
                    else:
                        #FAR MATCH
                        exists = 0
                        for rela in relations:
                            if ((rela['term1_id'] == sobj[0] and rela['term2_id'] == sobj2[0]) or (rela['term1_id'] == sobj2[0] and rela['term2_id'] == sobj[0])) and rela['type'] == "same article":                            
                                exists = 1    

                        if exists == 0:                              
                            if debug:
                                printflush("\nadd FAR relationship between "+sobj[1] +" (id: "+str(sobj[0])+") and "+sobj2[1] +" (id: "+str(sobj2[0])+")")

                            relations.append({'term1':sobj[1], 'term1_id':sobj[0], 
                                              'term2':sobj2[1], 'term2_id':sobj2[0], 'type':'same article'})
                        else:
                            if debug:
                                printflush("\tRELATION ARLEADY EXISTS LOCALLY SO DON'T ADD IT" )
                    
                    
            i = i + 1
        c = c + 1
    return relations

@timeout(100)
def handle_far_far_single(far_objs,relations,sentences,debug):
    if debug:
        printflush("FUNCTION: In Handle Far Far Extra Single with Far objs: ")
        printflush(far_objs)
        
    c = 0
    while c < len(far_objs) - 1:
        sobj = far_objs[c]
        sobj_sent = sobj[2]
        i = c + 1
        while i < len(far_objs):
            sobj2 = far_objs[i]
            sobj2_sent = sobj2[2]
            exists = 0
            if sobj[0] == sobj2[0]:
                if debug:
                    printflush("Found Same Entity: "+sobj[1] +" (id: "+str(sobj[0])+") and "+sobj2[1]+" (id: "+str(sobj2[0])+") at sentence: ["+str(sobj_sent)+", "+str(sobj2_sent)+"] so don't add!")
            else:
                
                if sobj_sent == sobj2_sent:
                    #SAME SENTENCE MATCH!
                    for rela in relations:
                        if ((rela['term1_id'] == sobj[0] and rela['term2_id'] == sobj2[0]) or (rela['term1_id'] == sobj2[0] and rela['term2_id'] == sobj[0])) and rela['type'] == "same sentence" and rela['sentence_num'] == sobj_sent:
                            exists = 1

                    if exists == 0:   
                        if debug:
                            printflush("\tadd SAME SENTENCE relationship between "+sobj[1] +" (id: "+str(sobj[0])+") and "+sobj2[1]+" (id: "+str(sobj2[0])+") at sentence: "+str(sobj_sent))
                        relations.append({'term1':sobj[1], 'term1_id':sobj[0], 
                                          'term2':sobj2[1], 'term2_id':sobj2[0], 'type':'same sentence', 
                                          'text_snippet':sentences[sobj_sent], 'sentence_num':sobj_sent})
                    else:
                        if debug:
                            printflush("\tRELATION ARLEADY EXISTS LOCALLY SO DON'T ADD IT")
                else:
                    #NEAR or FAR MATCH
                    if sobj2_sent > sobj_sent:
                        subtype = "post"                                
                        dist = sobj2_sent - sobj_sent
                    else:
                        subtype = "prior"                
                        dist = sobj_sent - sobj2_sent  
                        
                    if dist < 4:
                        #NEAR MATCH
                        exists = 0
                        for rela in relations:
                            if ((rela['term1_id'] == sobj[0] and rela['term2_id'] == sobj2[0]) or (rela['term1_id'] == sobj2[0] and rela['term2_id'] == sobj[0])) and rela['type'] == "near":                                                                           
                                exists = 1

                        if exists == 0: 
                            if subtype == 'prior':
                                if debug:
                                    printflush("\nadd PRIOR relationship between "+sobj[1] +" (id: "+str(sobj[0])+") and "+sobj2[1] +" (id: "+str(sobj2[0])+") at sentence: "+str([sobj2_sent,sobj_sent])  )
                                    
                                relations.append({'term1':sobj[1], 'term1_id':sobj[0], 
                                                  'term2':sobj2[1], 'term2_id':sobj2[0], 'type':'near', 'subtype':subtype, 'distance': str(dist), 
                                                  'text_snippet':" ".join(sentences[sobj2_sent:sobj_sent+1]), 'sentence_num':[sobj2_sent,sobj_sent]})
                            else:
                                if debug:
                                    printflush("\nadd NEXT relationship between "+sobj[1] +" (id: "+str(sobj[0])+") and "+sobj2[1] +" (id: "+str(sobj2[0])+") at sentence: "+str([sobj_sent,sobj2_sent]))

                                relations.append({'term1':sobj[1], 'term1_id':sobj[0], 
                                                  'term2':sobj2[1], 'term2_id':sobj2[0], 'type':'near', 'subtype':subtype, 'distance': str(dist), 
                                                  'text_snippet':" ".join(sentences[sobj_sent:sobj2_sent+1]), 'sentence_num':[sobj_sent,sobj2_sent]})
                        else:
                            if debug:
                                printflush("\tRELATION ARLEADY EXISTS LOCALLY SO DON'T ADD IT")
                    else:
                        #FAR MATCH
                        exists = 0
                        for rela in relations:
                            if ((rela['term1_id'] == sobj[0] and rela['term2_id'] == sobj2[0]) or (rela['term1_id'] == sobj2[0] and rela['term2_id'] == sobj[0])) and rela['type'] == "same article":                            
                                exists = 1    

                        if exists == 0:                              
                            if debug:
                                printflush("\nadd FAR relationship between "+sobj[1] +" (id: "+str(sobj[0])+") and "+sobj2[1] +" (id: "+str(sobj2[0])+")")

                            relations.append({'term1':sobj[1], 'term1_id':sobj[0], 
                                              'term2':sobj2[1], 'term2_id':sobj2[0], 'type':'same article'})
                        else:
                            if debug:
                                printflush("\tRELATION ARLEADY EXISTS LOCALLY SO DON'T ADD IT" )
                    
                    
            i = i + 1
        c = c + 1
    return relations    



def handle_single_add_extra_linkstwo(sentn, relations,ent_to_global,dis_entities,sentences, marked_as_slow, centerobj, debug):
	global global_entities
	#go through relations
	if debug:
		time_start = time.clock()
		print "\nETET IN HANDLE SINGLE ADD EXTRA LINKS TWO"
		print "ETET sentences ("+str(len(sentences))+")"
		print sentences
		print "ETET sent:"
		print sentn
		print "ETET relations ("+str(len(relations))+"):"
		print relations
		print "ETET ent_to_global"
		print ent_to_global
		print "ETET dis_entities ("+str(len(ent_to_global.keys()))+")"
		for d in dis_entities:
			printflush(d)
			for de in dis_entities[d]:
				printflush("\t"+de+" : "+ str(dis_entities[d][de])+ "..globalentid.."+str(ent_to_global[de]))


	if debug:
		smsent = [ r for r in relations if r['type'] == 'same sentence']    #TODO How to sort by first sentence_number!
		nrsent = [ r for r in relations if r['type'] == 'near']
		smartl = [ r for r in relations if r['type'] == 'same article']

		dictsi = [] 
		for a in range(len(sentences)):
			dictsi.append([])

		for t in dis_entities:
			for e in dis_entities[t]:
				for sn in dis_entities[t][e]['sentence']:
					snu = int(sn)
					add = ent_to_global[e]
					dictsi[snu].append(ent_to_global[e])

		if debug:
			printflush("Dictsi\n")
			for i,s in enumerate(dictsi):
				print "Sentence "+str(i)+ " has global entities: " + str(s)

		print "\n(((Same Sentences: "+str(len(smsent))
		for sm in smsent: print sm
		print "\n(((Near Sentences: "+str(len(nrsent))
		for sm in nrsent: print sm
		print "\n((Same Article: "+str(len(smartl))
		for sm in smartl: print sm

	#REMOVE ANY SAME ARTICLE IDS WHICH ALREADY OCCUR IN SAME SENTENCE OR NEAR RELATIONS ( SINCE ITS DOUBLE COUNTING )
	#centern = relations[0]['term1']
	#centernid = relations[0]['term1_id']
	try:
		centern, centernid = centerobj
	except:
		traceback.print_exc(file=sys.stdout)
		centern = relations[0]['term1']
		centernid = relations[0]['term1_id']
		print "Vers Poscentern: "+centern
		print "Vers Poscenterid: "+str(centernid)

	id_to_ent = dict([ (t,id) for id,t in ent_to_global.iteritems()])
	to_keep = id_to_ent.keys()
	if debug:
		print "\nId_to_Ent: "+str(id_to_ent)
	
	#TODO How to sort by first sentence_number so in print out for debug the sentences go up in order
	smsent = [ r['term2_id'] for r in relations if r['type'] == 'same sentence' and r['term1_id'] == centernid]    
	nrsent = [ r['term2_id'] for r in relations if r['type'] == 'near' and r['term1_id'] == centernid]
	smart_ids = [ r['term2_id'] for r in relations if r['type'] == 'same article' and r['term1_id'] == centernid]
	same_and_near_ids = smsent + nrsent
	double_counted_ids = list(set.intersection(set(smart_ids),set(same_and_near_ids)))
	if len(double_counted_ids) > 0:
		if debug:
			print "\n!!!Found Double Counts in Same Articles so removing: "+str(double_counted_ids)
                        for d in double_counted_ids:
				removepattern = {'term1':centern, 'term1_id':centernid, 'term2':id_to_ent[d], 'term2_id':d, 'type':'same article'}
				if debug:
					print "REMOVE PATTERN: "+str(removepattern)
				try:
					relations.remove( removepattern )	
				except:		
					#http://stackoverflow.com/questions/1235618/python-remove-dictionary-from-list
					try:
						relations[:] = [d for d in relations if d.get('term1_id') != centernid and d.get('term2_id') != d and d.get('type') != "same article"]
					except:
						traceback.print_exc(file=sys.stdout)
						print "ERROR: couldn't find above REMOVE PATTERN in relations or via get"



	#0. before anything remove center_node (YVONNE DAVIS) from a copy of dis_entities .. this is term1 from any of the relations
	disco = copy.deepcopy(dis_entities)
	del disco["PERSON"][centern]	

	if debug:
		print "After Disco"
		for d in disco:
			printflush(d)
			for de in disco[d]:
				printflush("\t"+de+" : "+ str(disco[d][de]) + "..globalentid.."+str(ent_to_global[de]))

	#1.make a dictionary from copy of dis_entities which is just ids, and sents[]  
		#( i.e., it will be a dictionary indexed by sentence number with each index being a vector of ids in that sentence )
	dictsi = [] #* (len(sentences))  #sentences are zero indexed
	for a in range(len(sentences)):
		dictsi.append([])

	if debug:
		print "\nLen dictsi: "+ str(len(dictsi))
	for t in disco:
		for e in disco[t]:
			for sn in disco[t][e]['sentence']:
				snu = int(sn)
				add = ent_to_global[e]
				dictsi[snu].append(ent_to_global[e])
				#if debug:
				#	print "ADD id: "+str(add)+" to sentence index "+ str(sn)
				#	print dictsi

	#id_to_ent = dict([ (t,id) for id,t in ent_to_global.iteritems()])
	#to_keep = id_to_ent.keys()

	if debug:
		printflush("Dictsi\n")
		for i,s in enumerate(dictsi):
			print "Sentence "+str(i)+ " has global entities: " + str(s)
					

	#2.then since we know there are no duplicates, start making all the couples that way ( start with  first sentence )  you just need to make sure you aren't combining two of the same id.
	nodes_handled = []
	same_articles = []
	for i,sen in enumerate(dictsi):
		if len(sen) == 0:
			continue
		else:
			samesent_seen = []
			for n,es in enumerate(sen):
				has_relation_with = []
				if es not in nodes_handled:
					esterm = id_to_ent[es]
					if debug:
						printflush("*** Currently adding rels for sent("+str(i)+"): Entity: "+esterm+"("+str(es)+")")
					#make same sent relations based on first peron
					for os in sen:
						if os != es and os not in samesent_seen:
							osterm = id_to_ent[os]
							if debug:
								printflush("\tadd SAME SENTENCE relationship between "+esterm +" (id: "+str(es)+") and "+ osterm +" (id: "+str(os)+") at sentence: "+str(i) )
							relations.append({'term1':esterm, 'term1_id':es, 
									  'term2':osterm, 'term2_id':os, 'type':'same sentence', 
									  'text_snippet':sentences[i], 'sentence_num':i})
							has_relation_with.append(os)
					samesent_seen.append(es)

					#make near sent relations
					#	1. make prior near
					start = i - 3
					if start < 0: start = 0
					while start < i:
						cursen = dictsi[start]	
						for curent in cursen:	
							if curent != es:
								subtype = "prior"                
								dist = i - start 
								osterm = id_to_ent[curent]
								if debug:
									printflush("\tadd Near prior relationship between "+esterm +" (id: "+str(es)+",sen: "+str(i)+") and "+ osterm +" (id: "+str(curent)+",sen: "+str(start)+") with dist: "+str(dist))
								relations.append({'term1':esterm, 'term1_id':es, 
										  'term2':osterm, 'term2_id':curent, 'type':'near', 'subtype':subtype, 'distance': str(dist), 
										  'text_snippet':" ".join(sentences[start:i+1]), 'sentence_num':[start,i]})
								has_relation_with.append(curent)
						start = start + 1

					#	2. make next near
					end = i + 3
					if end >= len(sentences): end = len(sentences) - 1
					try:
						while end > i:
							cursen = dictsi[end]	
							for curent in cursen:	
								if curent != es:
									subtype = "post"                
									dist = end - i 
									osterm = id_to_ent[curent]
									if debug:
										printflush("\tadd Near post relationship between "+esterm +" (id: "+str(es)+",sen: "+str(i)+") and "+ osterm +" (id: "+str(curent)+",sen: "+str(end)+") with dist: "+str(dist))
									relations.append({'term1':esterm, 'term1_id':es, 
											  'term2':osterm, 'term2_id':curent, 'type':'near', 'subtype':subtype, 'distance': str(dist), 
											  'text_snippet':" ".join(sentences[i:end+1]), 'sentence_num':[i,end]})
									has_relation_with.append(curent)
							end = end - 1
					except:
						print "ERROR Index issue with i: "+str(i)+" and end: "+str(end)+" and len of sentences is "+str(len(sentences))+ " and length of dictsi = "+str(len(dictsi))
						traceback.print_exc(file=sys.stdout)
						
					

					#make same article, based on everyone in to_keep who is not in curseen and is not es and hasn't been handled already ( since they've made same article relations already)
					same_art_ids = [aa for aa in to_keep if aa not in set(has_relation_with) and aa != es and  aa not in nodes_handled and aa != centernid]     #([aa,es] not in same_articles and [es,aa] not in same_articles)]
					if debug:
						print "\n\tADD same article relationship between "+str(es)+" and "+str(same_art_ids)

					for sai in same_art_ids:
						saiterm = id_to_ent[sai]
						if debug:
							printflush("\tadd Same article relationship between "+esterm+" ("+str(es)+") and "+saiterm+" ("+str(sai)+")")
                        			relations.append({'term1':esterm, 'term1_id':es, 'term2':saiterm, 'term2_id':sai, 'type':'same article'})
						#same_articles.append([es,aa])

					nodes_handled.append(es)
					
	
	#XXX (done in two) 3.then make the relations (same sent, near sent, same article ) and you are done ( this should go faster ).
	#4.try it out when you are done, with BOB since you can test him
	if debug:
		print "\nAfter Everything: Dis_Entities"
		for d in dis_entities:
			printflush(d)
			for de in dis_entities[d]:
				printflush("\t"+de+" : "+ str(dis_entities[d][de])+ "..globalentid.."+str(ent_to_global[de]))

		printflush("*******************************Dictsi\n")
		for i,s in enumerate(dictsi):
			print "Sentence "+str(i)+ " has global entities: " + str(s)
		print "\nLen of relations: "+str(len(relations))
		smsent = [ r for r in relations if r['type'] == 'same sentence']    #TODO How to sort by first sentence_number!
		nrsent = [ r for r in relations if r['type'] == 'near']
		smartl = [ r for r in relations if r['type'] == 'same article']
		print "\n(((Same Sentences: "+str(len(smsent))
		for sm in smsent: print sm
		printflush("*******************************Dictsi\n")
		for i,s in enumerate(dictsi):
			print "Sentence "+str(i)+ " has global entities: " + str(s)
		print "\n(((Near Sentences: "+str(len(nrsent))
		for sm in nrsent: print sm
		printflush("*******************************Dictsi\n")
		for i,s in enumerate(dictsi):
			print "Sentence "+str(i)+ " has global entities: " + str(s)
		print "\n((Same Article: "+str(len(smartl))
		for sm in smartl: print sm
		time_end = time.clock()
		print("HANDLE EXTRAS TIME INFORMATION: took "+str(time_end - time_start)+" seconds")

	return relations




@timeout(100)
def handle_single_add_extra_links(sentn, relations,ent_to_global,dis_entities,sentences, marked_as_slow, debug):
    global global_entities
    #poli_id = relations[0]['term1_id']
    if debug == debug:
        total_hsae_start = time.clock()
        printflush("FUNCTION: In Handle_Single_Add_Extra_links with sentn: "+str(sentn))
        
    #ssobjs = [ [r['term2_id'],r['term2'],r['sentence_num']] for r in relations if r['type'] == 'same sentence']
    #same_sentence_objs = [ [so[0],so[1],so[2]] for so in ssobjs if so[2] == sentn]
    
    #near_sentence_objs = [ [r['term2_id'],r['term2'],r['sentence_num'],r['subtype']] for r in relations if r['type'] == 'near']            
    #pr = [[p[0],p[1],p[2][0]] for p in near_sentence_objs if p[3] == 'prior' and p[2][1] == sentn]
    #po = [[p[0],p[1],p[2][1]] for p in near_sentence_objs if p[3] == 'post' and p[2][0] == sentn]
    #near_objs = pr + po            

    #saved = {}
    #far = [ [r['term2_id'],r['term2'],-1] for r in relations if r['type'] == 'same article' and str(r['term2_id'])+r['term2'] not in saved] 
    #far = []
    #for r in relations:
    #    if r['type'] == 'same article' and str(r['term2_id'])+"-"+r['term2'] not in saved:
    #        saved[str(r['term2_id'])+"-"+r['term2']] = 1
    #        far.append([r['term2_id'],r['term2'],-1])


    #this should be equivalent to the above
    same_sentence_objs = []
    pr = []
    po = []
    saved = {}
    far = []
    for r in relations:
	if r['type'] == 'same sentence' and r['sentence_num'] == sentn :
		same_sentence_objs.append([r['term2_id'],r['term2'],r['sentence_num']])
	elif r['type'] == 'near':
		if r['subtype'] == 'prior' and r['sentence_num'][1] == sentn:
			pr.append([r['term2_id'],r['term2'],r['sentence_num'][0]])	
		elif r['subtype'] == 'post' and r['sentence_num'][0] == sentn:
			po.append([r['term2_id'],r['term2'],r['sentence_num'][1]])	
    	elif r['type'] == 'same article' and str(r['term2_id'])+"-"+r['term2'] not in saved:
	        saved[str(r['term2_id'])+"-"+r['term2']] = 1
        	far.append([r['term2_id'],r['term2'],-1])
	
    near_objs = pr + po


    #make far unique, remove dupes
    #Nearobks:[[130, u'Tom Craddick', 9], [202, u'Jim Pitts', 9], [199, u'Democrats', 10], [37, u'Sylvester Turner', 13], [130, u'Tom Craddick', 13], [37, u'Sylvester Turner', 14]]
    #Far objs [[196, u'Texas House Democrats', 0], [199, u'Democrats', 1], [130, u'Tom Craddick', 1], [200, u'Democrat', 2], [130, u'Tom Craddick', 1], [130, u'Tom Craddick', 1], [130, u'Tom Craddick', 1], [130, u'Tom Craddick', 1], [130, u'Tom Craddick', 1], [130, u'Tom Craddick', 1]]
    
    if debug:
        printflush("Generating Far_objs dict")
        
    fobjs = []
    if marked_as_slow == False:
        for f in far:
            gid = ent_to_global[f[1]]
            gob = global_entities[gid]
            et = gob['entity_type']
            if et == "politician":       #why am i doing this??
                et = "PERSON"
            ss = []
            if f[1] not in dis_entities[et]:       #f1 is name of node, gid is its global id, gob is its global_entities obj, and et is its type.. dis_entities is index by "types"
                if debug:
                    printflush("$%$%$%$%$%$%$%$%$%ERROR: "+f[1]+ " not in type: "+et)
                    printflush("Dis_entities[et]:")
                    printflush(dis_entities[et])
                    printflush("All Dis_entities")
                    printflush(dis_entities)

                for tg in dis_entities:                 #i can make a lookup table and stop repeatedly looping over all the dis_entities instead (this won't save much since its only 5 indexes big)
                    if f[1] in dis_entities[tg]:
                        if debug:
                            printflush("Now Found "+f[1]+" in "+tg+" !")
                        ss = dis_entities[tg][f[1]]['sentence']

                if ss == []:
                    continue

            else:
                ss = dis_entities[et][f[1]]['sentence']

            if debug:
                printflush("Term: " +f[1] + ", Gid: "+str(gid) +", Gob:" + str(gob))
                printflush("Et:" + et + ", Sentence:" + str(ss))


            if len(ss) == 1:                    
                if debug:
                    printflush("ADDING: ("+str(f[0])+", "+f[1]+", "+str(ss[0])+") to fobjs")

                fobjs.append([f[0],f[1],ss[0]])
            else:
                if debug:
                    printflush("Found ss with multiple ids.")
                    #HANDLE by seeing if any of the sentences are farther than 2 * context away, and if so select 
                    #any since you can only have one "same article" reference for the given word anyways regardless of location

                    #In handle_single_add_extra_links with sentn: 6
                    #Term: Democrats, Gid: 199, Gob:{u'entity_type': u'MISC', u'id': [1, 9, 14, 15, 18, 19], 
                    #                                u'full_name': u'Democrats', u'sentence': [1, 4, 6, 7, 10, 12]}
                    #Et:MISC, Sentence:[1, 4, 6, 7, 10, 12]
                    #ERROR: found ss with multiple ids.. TODO: HOW TO HANDLE THIS.  for now don't include in far_objs
                poss = [x for x in ss if abs( x - sentn ) > 2 * number_sentences_for_context]     #number_sentences_for_context set in bottom of dama_utils
                if len(poss) > 0:
                   fobjs.append([f[0],f[1],poss[0]]) 

        if debug == debug:
            #printflush("Fobjs = ")
            #printflush(fobjs)

    	    total_hsae_pre_end = time.clock()
	    telapsed = (total_hsae_pre_end - total_hsae_start) / 60
	    printflush("IMPORTANT TIME STUFF:   pre-looking took: "+str(telapsed)+" minutes") 

        far_objs = [ [fo[0],fo[1],fo[2]] for fo in fobjs if abs( fo[2] - sentn ) > number_sentences_for_context ]        
    else:
        #if debug:
        printflush("THIS ARTICLE WAS MARKED AS SLOW SO DON't ADD relations to far items")   #is this actually being used the above optimizations do nothing :)
        far_objs = []
	if debug:
		total_hsae_pre_end = time.clock()
                
    ##MAKE SURE YOU HAVE THE CORRECT FAR ONES!
    #TODO find sentence nums for far sentences  <--- hERE, then see if a=5 works, then do multiple for this! !!            
    if debug:
        printflush("--OBJECTS GIVEN\nSame Sentence Objs [id,term,sentnum]")
        printflush(same_sentence_objs)
        printflush("\nNear Objs [id,term,sentnum]")
        printflush(near_objs)
        printflush("FAR:")
        printflush(far_objs)
        printflush("\nDisEntities:")
        printflush(dis_entities)
        printflush("\nEnt To global")
        printflush(ent_to_global)

    if len(same_sentence_objs) > 0:
        if debug:
            printflush("Add same sentence relations")

        #MATCH SAME SENTENCE WITH ONE ANOTHER   as SS
        if len(same_sentence_objs) > 1:
            relations = handle_same_extra_single(same_sentence_objs,relations,sentences,debug)

        if len(near_objs) > 0:
            #MATCH SAME SENTENCE WITH NEAR as NEAR
            relations = handle_same_near_extra_single(same_sentence_objs,near_objs,relations,sentences,debug)

        if len(far_objs) > 0:
            #MATCH SAME SENTENCE WITH FAR as FAR        
            relations = handle_same_far_extra_single(same_sentence_objs,far_objs,relations,sentences,debug)
    	
	if debug == debug:  
		total_hsae_pre_end2 = time.clock()
		telapsed = (total_hsae_pre_end2 - total_hsae_pre_end) / 60
		printflush("IMPORTANT TIME STUFF:   same sentence objs took: "+str(telapsed)+" minutes") 
    else:
	if debug == debug:
		total_hsae_pre_end2 = time.clock()


    if len(near_objs) > 0:
        if debug:
            printflush("Add near sentence relations")

        #MATCH NEAR WITH ONE ANOTHER as either SS or NEAR depending
        if len(near_objs) > 1:
            relations = handle_near_near_single(near_objs,relations,sentences,debug)

	if debug == debug:  
		total_hsae_pre_end3a = time.clock()
		telapsed = (total_hsae_pre_end3a - total_hsae_pre_end2) / 60
		printflush("IMPORTANT TIME STUFF:   near objs handle near near took: "+str(telapsed)+" minutes") 

        if len(far_objs) > 0:
            #MATCH NEAR with FAR depending as NEAR or Far
            relations = handle_near_far_single(near_objs,far_objs,relations,sentences,debug)

	if debug == debug:  
		total_hsae_pre_end3b = time.clock()
		telapsed = (total_hsae_pre_end3b - total_hsae_pre_end3a) / 60
		printflush("IMPORTANT TIME STUFF:   near objs near far far took: "+str(telapsed)+" minutes") 
    else:
	if debug:
		total_hsae_pre_end3 = time.clock()
            
    if len(far_objs) > 1:
        if debug:
            printflush("Add far far sentence relations")

        #MATCH FAR WITH ANOTHER as either SS, NEAR, or FAR depending        
        relations = handle_far_far_single(far_objs,relations,sentences,debug)
	if debug == debug:  
		total_hsae_pre_end4 = time.clock()
		telapsed = (total_hsae_pre_end4 - total_hsae_pre_end3b) / 60
		printflush("IMPORTANT TIME STUFF:   far objs took: "+str(telapsed)+" minutes") 
        
    if debug == debug:  
	total_hsae_pre_end5 = time.clock()
	telapsed = (total_hsae_pre_end5 - total_hsae_start) / 60
	printflush("VERY IMPORTANT TIME STUFF:   OVERALL function took: "+str(telapsed)+" minutes") 

    return relations
