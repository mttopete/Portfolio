from threading import Lock
def init():
    global longest_page 
    global word_frequency 
    global unique_urls 
    global ics_urls 
    global f_mutex
    global ics_uci_edu_mutex 
    global cs_uci_edu_mutex 
    global stat_uci_edu_mutex 
    global today_uci_edu_mutex 
    global informatics_uci_edu_mutex
    global lp_mutex
    global wf_mutex
    global uu_mutex
    global iu_mutex
    global stopwords

    longest_page = 0
    word_frequency = {}
    unique_urls = set()
    ics_urls = {}
    f_mutex = Lock()
    ics_uci_edu_mutex = Lock()
    cs_uci_edu_mutex = Lock()
    stat_uci_edu_mutex = Lock()
    today_uci_edu_mutex = Lock()
    informatics_uci_edu_mutex = Lock()
    lp_mutex = Lock()
    wf_mutex = Lock()
    uu_mutex = Lock()
    iu_mutex = Lock()
    stopwords = ["a","about","above","after","again","against","all","am","an","and","any","are","aren't","as","at",
                 "be","because","been","before","being","below","between","both","but","by"
                 "can't","cannot","could","couldn't",
                 "did","didn't","do","does","doing","don't","down","during",
                 "each",
                 "few","for","from","further",
                 "had","hadn't","has","hasn't","have","haven't","having","he","he'd","he'll","he's","her","here","here's",
                 "hers","herself","him","himself","his","how","how's",
                 "i","i'd","i'll","i'm","i've","if","in","into","is","isn't","it","it's","its","itself",
                 "lets","me","more","most","mustn't","my","myself",
                 "no","nor","not","of","off","on","once","only","or","other","ought","our","ours",
                 "ourselves","out","over","own","same","shan't","she","she'd","she'll","she's","should","shouldn't",
                 "so","some","such","than","that","that's","the","their","theirs","them","themselves","then","there",
                 "there's","these","they","they'd","they'll","they're","they've","this","those","through","to","too",
                 "under","until","up","very","was","wasn't","we","we'd","we'll","we're","we've","were","weren't","what",
                 "what's","when","when's","where","where's","which","while","who","who's","whom","why","won't","would","wouldn't",
                 "you","you'd","you'll","you're","you've","your","yours","yourself","yourselves"]
