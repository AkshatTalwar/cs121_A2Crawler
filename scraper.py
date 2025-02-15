import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin, urldefrag

import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def scraper(url, resp):
    if not resp.raw_response or not resp.raw_response.content:
        logging.warning(f"No content at {url}")
        return []
    logging.info(f"Scraping {url}")
    links = extract_next_links(url, resp)
    logging.info(f"Found {len(links)} links at {url}")


def extract_next_links(url, resp):
    if resp.status != 200 or not resp.raw_response:
        logging.error(f"Error encountered for {url}: {resp.status}")
        return []

    try:
        html_content = resp.raw_response.content.decode("utf-8", errors="ignore")
        soup = BeautifulSoup(html_content, "html.parser")
    except Exception as e:
        logging.error(f"Failed to parse HTML for {url}: {e}")
        return []

    # Determine the base URL for resolving relative links
    base_tag = soup.find("base", href=True)
    if base_tag:
        base_url = base_tag["href"]
    else:
        base_url = url

    links = set()
    for tag in soup.find_all("a", href=True):
        try:
            absolute_url = absolute_url.encode("ascii").decode("ascii")  # Ensure ASCII
            links.add(absolute_url)
        except UnicodeEncodeError:
            continue

    logging.info(f"Extracted {len(links)} raw links from {url}")
    return sorted(links)


def is_valid(url):
    try:
        parsed = urlparse(url)

        if parsed.scheme not in {"http", "https"}:
            return False

        allowed_domains = {".ics.uci.edu", ".cs.uci.edu", ".informatics.uci.edu", ".stat.uci.edu"}
        if not any(parsed.netloc == domain or parsed.netloc.endswith(domain) for domain in allowed_domains):
            return False

        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print("TypeError for ", url)
        raise