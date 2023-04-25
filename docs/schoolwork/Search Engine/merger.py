#55394 total documents
import os
import sys
import pickle 
import math
import numpy as np
#$os.chdir("/home/mttopete/Assignment3/indexes")
files = 0
path = "/home/mttopete/Assignment3/indexes"
os.chdir(path)
types = ["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z","#"]
parts = math.floor((len(os.listdir()))/27) #find the amount of partial indexes per letter
total_docs = 55394
indexindex = {}
place_in_text_file = 0
f = open("Words.txt","w")
for letter in types:
    working_dicts = []
    for n in range(1,parts+1):
        working_dicts.append(pickle.load( open(f"{letter}{n}.p","rb") ))
    complete = {}
    for d in range(parts):  #for every dictionary we are currently working with
            cd = working_dicts.pop()#pop out a partial dictionary
            for word in cd.keys(): #for every word in that dictionary
                for x in working_dicts: #for every remaining dictionary
                    try:
                        for post in x[word]: #try to get the postings for that word in each remaining dictionary
                            cd[word].append(post) #append each posting
                        x.pop(word) #pop the word out so that it is not repeated
                    except:
                        pass #if the word doesnt exist in that partition, do nothing
            complete.update(cd) #update the complete dictionary
            del(cd) #delete the used up dictionary to free space and keep everything clean
    #now, once a complete dictionary of all words and their postings has been made, calculate the tf-idf score for each document
    #into a long string that will be the entry in the master text file
    for word,post_list in complete.items():
        print(word)
        added_string = ""
        total_posts = len(post_list)
        for tup in post_list:
            base_wtf = (1+np.log(tup[1])) #pre-compute the weighted tf score (for LNC.LTC as described in lecture)
            total_wtf = base_wtf
            total_wtf += base_wtf*0.15*tup[2] #+ 15% weight if the word was bold
            total_wtf += base_wtf*0.15*tup[3] #+ 15% weight if the word was a header
            total_wtf += base_wtf*0.15*tup[4] #+ 15% weight if the word was in the title
            added_string += f"{tup[0]},{total_wtf};" #each posting will be semicolon separated and within that the fid and wtf score will be comma separated
        added_string += "\n" #add a newline to the word postings string
        f.write(added_string)
        indexindex[word] = (place_in_text_file,total_posts) #document where in the text file the postings for this word begin as well as the document frequency for LNC.LTC
        place_in_text_file += len(added_string) #update the starting place for the next word
    pickle.dump( indexindex, open( "indexindex.p", "wb" ) )
    
f.close()
print("now, pray to tim")