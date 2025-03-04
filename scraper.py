#TA Permission added gihub
# create and initialise the project: Akshat
# tokenise updated from A1 by: Sanaa
# Traps detection: Suyash and Akshat
# Simhash learned via net and modified version via Akshat
# Validity of our domains tht crawler went to : Arsheaa
# scrapers error code handling : Suyash
# combining scraper with functions everyone
# tracking unique pages and sending tokeniser is working via Sanaa
# Log saver and loader via saving to json: Suyash
# Defragging the links and making sure we don't go to fragments in our Crawl
# Rebasing and stashing via everyone
# robots.txt implemented by suyash and arsheaa but removed coz not reading too many pages

import re
import json
# import urllib.robotparser
# from urllib.parse import urlparse
from urllib.parse import urljoin, urlparse, urldefrag
from bs4 import BeautifulSoup
from tokenizer import tokenize
from collections import deque
from simhash_basic import make_simhash, simhash_diff


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
TRAP_PATTERNS = [
    r'\?sort=', r'\?order=', r'\?page=\d+',  # URLs
    r'\?date=', r'\?filter=', r'calendar', r'\?view=', r'\?session=', # calender
    r'\?print=', r'\?lang=', r'\?mode=', r'\?year=\d{4}', r'\?month=\d{1,2}', r'\?day=\d{1,2}',
    r'\?tribe-bar-date=', r'outlook-ical=',  #  infinite event/calendar URLs
    r'\.ical$', r'\.ics$',  # Blocks iCalendar/ICS downloads
    r'doku\.php',  # Blocks all doku.php pages , worst!!! trap
    r'\?do=media', r'\?tab_details=', r'\?tab_files=',
    r'\?rev=\d+',
    r'&do=diff',
    r'&do=edit',
    r'&printable=yes',
    r'\?share=',
    r'\?replytocom=',
    r'\?fbclid=', r'utm_',  # analytics from fb and some gooogle
    r'\?redirect=',  # auto-redirects that could loop infinitely
    r'\?attachment_id=',  # media
]
# robots_parsers = {}
# Robots.txt sometimes stop our program from going to desired pages causing 0 crawls issue so rn commented
# Dictionary to store parsed robots.txt per domain
# robots_parsers = {}
# def can_fetch(url):
#     """Checks if the URL is allowed by robots.txt"""
#     # the format learned from stacko.flow
#     parsed = urlparse(url)
#     domain = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
#     # Load txt
#     if domain not in robots_parsers:
#         rp = urllib.robotparser.RobotFileParser()
#         rp.set_url(domain)
#         try:
#             rp.read()  # read robots.txt
#             robots_parsers[domain] = rp
#         except Exception as e:
#             print(f"couldn't find robots.txt")
#             return True # continue crawl
#
#     # so now we have checked
#     return robots_parsers[domain].can_fetch("*", url)

def is_trap(url):
    """Detects common crawler traps based on URL patterns."""
    parsed = urlparse(url)
    # somehow came in even when we removed from traps
    if "doku.php" in parsed.path:
        return True
    # patterns
    for i in TRAP_PATTERNS:
        if re.search(i, url):
            return True
    return False

def is_similar(text):
    #Checks if a page is too similar
    page_hash = make_simhash(text)
    for old_hash in visited_hashes:
        if simhash_diff(page_hash, old_hash) < 5:  # Adjust threshold as needed
            return True  # Too similar, skip
    visited_hashes.add(page_hash)
    return False

def scraper(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content

    global longest_page # longest page

    # 1.to deal with weird 600 codes
    if 600 <= resp.status < 700:
        print(f"Skipping URL due to unknown 601 error (status {resp.status}): {url}")
        return []

    # 2. redirects from 300s
    if 300 <= resp.status <= 399:
        new_url = resp.raw_response.headers.get("Location")
        if new_url:
            print(f"Redirecting {url} - {new_url}")
            return [new_url]  # goes to next direct
        else:
            print(f"Skipping redirect : {url}") # couldnt find so left
            return []

    # 2. response status is 300
    if resp.status != 200 or resp.raw_response is None:
        return []

    # 3. Too long of a page
    if len(resp.raw_response.content) > MAX_PAGE_SIZE:
        print(f"Skipping large file (>1MB): {url}")
        return []

    # 4. is a trap ????
    if is_trap(url):
        print(f"Skipping potential crawler trap: {url}")
        return []

    # 5. Parsing the pages text
    soup = BeautifulSoup(resp.raw_response.content, "html.parser")
    text_content = soup.get_text()

    # -> 5.1 Check for duplicate content our (SimHash)
    if is_similar(text_content):
        print(f"Skipping duplicate page: {url}")
        return []

    # -> 5.2 Avoid low-content pages around 50 words
    word_count = len(text_content.split())
    if word_count < MIN_WORD_COUNT:
        print(f"Skipping low-content page (<50 words): {url}")
        return []

    # 6 . we process i.e. tokens
    tokens = tokenize(text_content)
    update_word_counts(tokens)

    # 7. we update our longest page again
    if word_count > longest_page[1]:
        longest_page = (url, word_count)

    # 8 make sure our unique pages are saved in logs
    track_unique_pages(url)

    # 9. Extract and validate links
    links = extract_next_links(url, soup)
    valid_links = [link for link in links if is_valid(link)]

    # 10. Add new valid links to the queue**
    for link in valid_links:
        if link not in visited_urls:
            visited_urls.add(link)
            url_queue.append(link)

    # 11. needs our log function!
    save_log() # saves progress
    return valid_links

def extract_next_links(url, soup):
    # next links in to be extracted from current url/soup
    links = []
    for tag in soup.find_all("a", href=True):
        absolute_url = urljoin(url, tag["href"])
        absolute_url, _ = urldefrag(absolute_url) # no frag
        links.append(absolute_url)
    return links


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
        return True
    except TypeError:
        print ("TypeError for ", parsed)
        raise

def track_unique_pages(url):
    #Tracks unique visited pages and subdomains
    global visited_urls, subdomains

    parsed = urlparse(url)
    domain = parsed.netloc

    if url not in visited_urls:
        visited_urls.add(url)
        if domain in subdomains:
            subdomains[domain] += 1
        else:
            subdomains[domain] = 1

def update_word_counts(tokens):
   # updates our count of words
    global word_counts
    for word in tokens:
        word_counts[word] = word_counts.get(word, 0) + 1


def save_log():
    """Saves to our log.json."""
    log_data = {
        "visited_urls": list(visited_urls),
        "word_counts": word_counts,
        "subdomains": subdomains,
        "longest_page": longest_page
    }
    with open(LOG_FILE, "w") as file:
        json.dump(log_data, file)

def load_log():
    """Loads from the previous crawl's .json."""
    global visited_urls, word_counts, subdomains, longest_page
    try:
        with open(LOG_FILE, "r") as file:
            log_data = json.load(file)
            visited_urls = set(log_data["visited_urls"])
            word_counts.update(log_data["word_counts"])
            subdomains.update(log_data["subdomains"])
            longest_page = tuple(log_data["longest_page"])
            print("Previous crawl state loaded.")

    except FileNotFoundError:
        print("No previous log file found. Starting fresh crawl.")

    except Exception as e:
        print(f"Error loading log file: {e}")
