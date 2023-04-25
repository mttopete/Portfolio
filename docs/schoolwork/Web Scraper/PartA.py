import sys
import stat_tracker as st
"""
tokenize runs in O(N) time.

the function passes over the file of lengh N exactly one time
It does check each character for being alphanumeric and ascii(to make sure its english and not say, japanese)
however the extra time needed is trivial as the file size becomes large

A try-except statement ensures a file can open safely.
Characters are read one by one and concatenated into a token
upon reaching a non-alphanumeric or non ascii(english) character
the token is considered complete and is then added to the list of tokens
as an all lowercase string to make sure capitalization does not matter
"""
def tokenize(text):
    tokens = []
    token = ""
    word_count = 0
    for c in text:
        char = c
        if char.isalnum() != True and char != "’":
            if char == '':
                if(token != '' and len(token) > 1):
                    word_count += 1
                    tokens.append(token.lower())
            else:
                if(token != "" and len(token) > 1):
                    word_count += 1
                    tokens.append(token.lower())
                token = ""
        else:
            token += char
    st.lp_mutex.acquire()
    if(word_count > st.longest_page):
        st.longest_page = word_count
    st.lp_mutex.release()
    return tokens
"""
The time complexity for this function is O(N)

python dictionaries rely on a hash map so accessing and writing to the dictionary
happens in O(1) time. Thus, we are limited by the size of the token list
which we only iterate through once.
"""
def computeWordFrequencies(token_list):
    st.wf_mutex.acquire()
    for token in token_list:
        try:
            st.word_frequency[token] += 1
        except:
            st.word_frequency[token] = 1
    st.wf_mutex.release()


def printFrequencies(token_map):
    sorted_map = sorted(token_map,key = lambda token: token_map[token],reverse = True)
    x = 0
    for token in sorted_map:
        x += 1
        print(token," - ",token_map[token])
        if x == 50:
            return
