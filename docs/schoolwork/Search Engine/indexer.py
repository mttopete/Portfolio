import os
from bs4 import BeautifulSoup
import parser
import sys
import pickle 
from nltk.stem import PorterStemmer
import re
path = "/home/mttopete/Assignment3/DEV"
index_dir = "/home/mttopete/Assignment3/indexes"
os.chdir(path)
fid = 0
files = 0
indexeption = {}
url_index = {}
global offload_num
offload_num = 0
ps = PorterStemmer()
global partitions
partitions = {x:{} for x in ["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z","#"]}

def offload():
    global offload_num
    global partitions
    os.chdir(index_dir)
    offload_num += 1
    for part_dict in partitions.keys():
        pickle.dump( partitions[part_dict], open( f"{part_dict}{offload_num}.p", "wb" ) )
    del(partitions)
    partitions = {x:{} for x in ["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z","#"]}
    os.chdir(path)
    return

    
for folder in os.listdir():
    files += 1
    folder_path = f"{path}/{folder}"
    os.chdir(folder_path)
    print("Now doing folder ",files)
    for file in os.listdir():
        fid += 1
        file_path = f"{folder_path}/{file}"
        tokens,bolds,headings,titles = parser.tokenize(file_path)
        url_index[fid] = tokens[1]
        stokens = [ps.stem(re.sub(r'\W+', '', x).lower()) for x in tokens]
        frequencies = parser.computeWordFrequencies(stokens)
        for word,freq in frequencies.items():
            bold = 0
            head = 0
            title = 0
            if word in bolds:
                bold = 1
            if word in headings:
                head = 1
            if word in titles:
                title = 1
            new_posting = (fid,freq,bold,head,title)
            if word[0] in partitions.keys():
                try:
                    partitions[word[0]][word].append(new_posting)
                except:
                    partitions[word[0]][word] = [new_posting]
            else:
                try:
                    partitions["#"][word].append(new_posting)
                except:
                    partitions["#"][word] = [new_posting]
        s = 0
        for d in partitions.keys():
            s += sys.getsizeof(partitions[d])
        if s >= 6000000:
            print("offloading")
            offload()
    print("Size after indexing folder:",s)

    
print("offloading remaining indexes")
offload()
print("total number of files:",fid)
os.chdir(index_dir)
pickle.dump( url_index, open( "urlindex.p", "wb" ) )