import pickle
import sys
import os
from nltk.stem import PorterStemmer
import math
import numpy as np
import time
import re
ps = PorterStemmer()

os.chdir("/home/mttopete/Assignment3/indexes")
indexindex = pickle.load( open( "indexindex.p", "rb" ) )
urlindex = pickle.load( open( "urlindex.p", "rb" ) )
f = open("Words.txt","r")

running = True

while running:
    print("Search: ",end = "")
    inp = input()
    t = time.thread_time()
    inp = inp.lower()
    inp = inp.split(" ")
    for x in range(len(inp)):
        inp[x] = re.sub(r'\W+', '', inp[x])
    scores = {}
    query_terms = {}
    if len(inp) > 1:
        for word in inp: #compute word freqencies for the query
            word = ps.stem(word)
            try:
                query_terms[word] += 1
            except:
                query_terms[word] = 1

        for k,v in query_terms.items():
            try:
                query_terms[k] = (1+np.log(v))*np.log(55394/indexindex[k][1]) #compute tf-idf for query
            except:
                query_terms[k] = 0
        doc_length = 0
        for k,v in query_terms.items():
            doc_length += v**2
        doc_length = math.sqrt(doc_length)
        cp_d = query_terms.copy()
        for k,v in cp_d.items():    #pre-compute the normalized vector for the query to use in the cosine similarity
            try:
                nmlz = v/doc_length
                if nmlz > 0.16:
                    query_terms[k] = nmlz
                else:
                    query_terms.pop(k)
            except:
                query_terms.pop(k)
        #now, parse through all query term's lines in the text file and score them
        for k in query_terms.keys():
            try:
                f.seek(indexindex[k][0])
                postingline = f.readline()
                postings = postingline.split(";")
                for z in postings:
                    if len(z) > 1:
                        zs = z.split(",")
                        x = zs[0]
                        y = zs[1]
                        try:
                            scores[x][k] = query_terms[k]
                        except:
                            scores[x] = {}
                            scores[x][k] = query_terms[k]
            except:
                scores[-1] = {}
                scores[-1][k] = query_terms[k]
        scored_fids = {}
        for fid,sl in scores.items():
            s = 0
            for k,v in query_terms.items():
                try:
                    s += query_terms[k]*scores[fid][k]
                except:
                    s += 0
            if s > .3:
                scored_fids[fid] = s
        sorted_scores = sorted(scored_fids.keys(), key=lambda x: scored_fids[x],reverse=True)
        printed_urls = []
        if len(sorted_scores) > 1:
            x = 0
            num_printed = 0
            while num_printed < 5:
                try:
                    if urlindex[int(sorted_scores[x])] not in printed_urls:
                        print(urlindex[int(sorted_scores[x])])
                        x += 1
                        num_printed += 1
                        printed_urls.append(urlindex[int(sorted_scores[x])])
                    else:
                        x += 1
                except:
                    num_printed = 5
        else:
            print("There are no matches for that query")
        print("Results in:",time.thread_time()-t)
    else:
        try:
            scores = {}
            f.seek(indexindex[ps.stem(inp[0])][0])
            postingline = f.readline()
            postings = postingline.split(";")
            for z in postings:
                if len(z) > 1:
                    zs = z.split(",")
                    x = zs[0]
                    y = zs[1]
                    scores[x] = y
            sorted_scores = sorted(scores.keys(), key=lambda x: scores[x],reverse=True)
            printed_urls = []
            if len(sorted_scores) > 1:
                x = 0
                num_printed = 0
                while num_printed < 5:
                    try:
                        if urlindex[int(sorted_scores[x])] not in printed_urls:
                            print(urlindex[int(sorted_scores[x])])
                            x += 1
                            num_printed += 1
                            printed_urls.append(urlindex[int(sorted_scores[x])])
                        else:
                            x+=1
                    except:
                        num_printed = 5
            else:
                print("There are no matches for that query")
        except:
            print("There are no matches for that query")
        print("Results in:",time.thread_time()-t)
        