import os
from bs4 import BeautifulSoup
from nltk.stem import PorterStemmer

ps = PorterStemmer()

def tokenize(file_path):
    try:
        reading = open(file_path,'r',encoding="utf-8")
        raw_text = reading.read()
        soup = BeautifulSoup(raw_text,'lxml')
        complete_token = ""
        skipnext = False
        token_list = []
        complete_token = ""
        skip = False
        for char in soup.get_text():
            try:
                char.encode("ascii")
            except:
                skip = True
            if skip == True:
                skip = False
            else:
                if char == "\\":
                    skip = True
                else:
                    if char in [""," ","\n"]:
                        if complete_token not in [""," "]:
                            token_list.append(complete_token)
                        complete_token = ""
                    else:
                        if len(complete_token) > 1 and char.isupper() == True and complete_token[1].isupper() == False:
                            if complete_token not in [""," "]:
                                token_list.append(complete_token)
                            complete_token = ""
                        complete_token += char

        bolds = set()
        for thing in soup.find_all('b'):
            try:
                for word in thing.string.split():
                    bolds.append(re.sub(r'\W+', '', ps.stem(word)))
            except:
                pass
        for thing in soup.find_all('strong'):
            try:
                for word in thing.string.split():
                    bolds.append(re.sub(r'\W+', '', ps.stem(word)))
            except:
                pass    

        headings = set()

        for thing in soup.find_all('h1'):
            try:
                for head in thing.string.split():
                    headings.add(re.sub(r'\W+', '', ps.stem(head)))
            except:
                pass

        for thing in soup.find_all('h2'):
            try:
                for head in thing.string.split():
                    headings.add(re.sub(r'\W+', '', ps.stem(head)))
            except:
                pass
        for thing in soup.find_all('h3'):
            try:
                for head in thing.string.split():
                    headings.add(re.sub(r'\W+', '', ps.stem(head)))
            except:
                pass

        try:
            title = [ps.stem(re.sub(r'\W+', '', word)) for word in soup.title.string.split()]
        except:
            title = []
        return token_list,bolds,headings,title
    except:
        return ["x","x"],[],[],[]


def computeWordFrequencies(token_list):
    word_frequency = {}
    for token in token_list:
        if "/" not in token and len(token) > 1:
            try:
                word_frequency[token] += 1
            except:
                word_frequency[token] = 1
    return word_frequency
