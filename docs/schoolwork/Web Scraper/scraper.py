import PartA
import stat_tracker as st
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from urllib import robotparser
def scraper(url, resp):
    if 200<= resp.status <= 206:
        parsed = urlparse(url)
        soup = BeautifulSoup(resp.raw_response.text,'html.parser')
        no_frag_url = parsed.netloc + parsed.path
        st.uu_mutex.acquire()
        st.unique_urls.add(no_frag_url)
        st.uu_mutex.release()
        PartA.computeWordFrequencies(PartA.tokenize(soup.get_text()))
        links = extract_next_links(url, resp)
        if url.find(".ics.uci.edu") > 0:
            st.iu_mutex.acquire()
            try:
                st.ics_urls[parsed.netloc] += 1
            except:
                st.ics_urls[parsed.netloc] = 1
            finally:
                st.iu_mutex.release()
        return [link for link in links if is_valid(link)]
    else:
        return []

def extract_next_links(url, resp):
    links = []
    rbp = robotparser.RobotFileParser(url)
    got_robots = True
    try:
        rbp.read()
    except:
        got_robots = False
        pass
    soup = BeautifulSoup(resp.raw_response.text,'html.parser')
    last_link = "placehold"
    for link in soup.find_all('a'):
        if (link.get('href') != None):
            link_text = link.get('href').split("/")
            add_link = True
            if (similarity(last_link,link.get('href')) > 0.9):
                add_link = False
            if(similarity(url,link.get('href')) >0.9):
                add_link = False
            for part in link_text:
                if part in set(["pdf"]):  #,"profiles","courses","student-profiles"]):
                    add_link = False
            for ignored in ["#comment","share=facebook","share=twitter","share=google-plus","replytocom"]:
                if link.get('href').find(ignored) > 0:
                    add_link = False
                if not rbp.can_fetch("*",link.get('href')) and got_robots == True:
                    add_link = False
            if add_link == True:
                links.append(link.get('href'))
            if(len(link.get('href')) > 0):
                last_link = link.get('href')
    return links

def is_valid(url):
    try:
        parsed = urlparse(url)
        valids = [".ics.uci.edu/", ".cs.uci.edu/",".informatics.uci.edu/",".stat.uci.edu/","today.uci.edu/department/information_computer_sciences/"]
        good = False
        for x in valids:
            if url.find(x) > 0:
                good = True
        if not good:
            return False
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|c|r|m|ppsx|py"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise

def similarity(url_1,url_2):
    reg = max(len(url_1),len(url_2))
    sim_score = 0
    for letter in range(0,reg-1):
        try:
            if url_1[letter] == url_2[letter]:
                sim_score += 1
        except:
            sim_score -= 1
    return sim_score/reg
