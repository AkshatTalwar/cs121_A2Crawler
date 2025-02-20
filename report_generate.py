import json
from collections import defaultdict, Counter
from urllib.parse import urlparse

def load_json(f):
    #reads a json file and returns its contents as a dictionary
    with open(f, "r", encoding="utf-8") as file:
        return json.load(file)

def get_unique_page_count(urls):
    # counts no. of unique pages crawled
    return len(set(urls))

def get_longest_page(f):
    # gets longest page link on the basis of the no. of words in it
    try:
        with open(f, "r", encoding="utf-8") as file:
            last_line = file.readlines()[-1].strip()  # Reads the last line

        return json.loads(last_line).get("longest_page", "Longest page data not found.")

    except (json.JSONDecodeError, IndexError, FileNotFoundError) as e:
        return f"Error reading longest page: {str(e)}"

def get_subdomains(urls):
    # gets unique pages per subdomain under 'ics.uci.edu'
    # uses dictionary to store each subdomain and its pages
    subdomains = defaultdict(set)
    for url in urls:
        parsed = urlparse(url)
        if "ics.uci.edu" in parsed.netloc:
            subdomains[parsed.netloc].add(url)
    return sorted(((sub, len(pages)) for sub, pages in subdomains.items()), key=lambda x: x[0])

def get_most_common_words(word_counts, top_n=50):
    # finds top 50 most common words from the crawled data
    return sorted(((w, c) for w, c in word_counts.items() if len(w) > 1 and not w.isdigit()),
                  key=lambda x: x[1], reverse=True)[:top_n]


if __name__ == "__main__":
    f = "crawler_log.json"
    data = load_json(f)
    urls, contents, word_counts = data.get("visited_urls", []), data.get("page_contents", []), data.get("word_counts",
                                                                                                        {})
    print(f"Unique pages: {get_unique_page_count(urls)}")
    print(f"Longest page: {get_longest_page(f)}")

    print("Subdomains in ics.uci.edu:")
    for sub, count in get_subdomains(urls):
        print(f"{sub}: {count}")

    print("\nTop 50 Most Common Words:")
    for word, count in get_most_common_words(word_counts):
        print(f"{word}: {count}")
