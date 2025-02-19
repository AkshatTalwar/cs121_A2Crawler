import re
from urllib.parse import urlparse

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
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
            return False

    except TypeError:
        print ("TypeError for ", parsed)
        raise
