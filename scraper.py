import re
from collections import deque
from urllib.parse import urlparse

MIN_WORD_COUNT = 50
MAX_PAGE_SIZE = 1 * 1024 * 1024  # 1MB in size
visited_urls = set()
visited_hashes = set()
LOG_FILE = "crawler_log.json"
subdomains = {}
word_counts = {}
longest_page = (None, 0)  # (URL, word count)
url_queue = deque()
STOPWORDS = set("""
a about above after again against all am an and any are aren't as at be because been before being below between both but by can't cannot could couldn't did didn't do does doesn't doing don't down during each few for from further had hadn't has hasn't have haven't having he he'd he'll he's her here here's hers herself him himself his how how's i i'd i'll i'm i've if in into is isn't it it's its itself let's me more most mustn't my myself no nor not of off on once only or other ought our ours ourselves out over own same shan't she she'd she'll she's should shouldn't so some such than that that's the their theirs them themselves then there there's these they they'd they'll they're they've this those through to too under until up very was wasn't we we'd we'll we're we've were weren't what what's when when's where where's which while who who's whom why why's with won't would wouldn't you you'd you'll you're you've your yours yourself yourselves""".split())



def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    global longest_page # longest page

    if 600 <= resp.status < 700: # 1.to deal with weird 600 codes
        print(f"Skipping URL due to unknown 601 error (status {resp.status}): {url}")
        return []

    #2. redirects from 300s
    if 300 <= resp.status <= 399:
        new_url = resp.raw_response.headers.get("Location")
        if new_url:
            print(f"Redirecting {url} - {new_url}")
            return [new_url]  # goes to next direct
        else:
            print(f"Skipping redirect : {url}") # couldnt find so left
            return []

    if resp.status != 200 or resp.raw_response is None: # 2. response status is 200
        return []

    if len(resp.raw_response.content) > MAX_PAGE_SIZE:# 3. Too long of a page
        print(f"Skipping large file (>1MB): {url}")
        return []

    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    return list()

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False

        # our allowed domains
        allowed_domains = [
            ".ics.uci.edu",
            ".cs.uci.edu",
            ".informatics.uci.edu",
            ".stat.uci.edu"
        ]
        if not any(parsed.netloc.endswith(domain) for domain in allowed_domains):
            return False

        if re.match(
                r".*\.(css|js|bmp|gif|jpg|jpeg|png|pdf|ico"
                + r"|tiff?|mid|mp2|mp3|mp4|wav|avi|mov|mpeg|m4v|mkv|ogg|ogv"
                + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx"
                + r"|data|dat|exe|bz2|tar|msi|bin|7z|dmg|iso"
                + r"|epub|dll|cnf|tgz|sha1|thmx|mso|arff|rtf|jar|csv"
                + r"|rm|smil|wmv|swf|wma|zip|rar|gz|ical|ppsx|pps|mol)$",
                parsed.path.lower()):
            # we added more extensions we learned from ed and trials
            return False

    except TypeError:
        print ("TypeError for ", parsed)
        raise
