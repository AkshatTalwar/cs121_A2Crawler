import sys
import re

Token = ""

STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during", "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when", "when's", "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves"
}

def tokenize(text: str) -> list[Token]:
    regex_pattern = re.compile(r"[A-Za-z0-9]+")
    return [word.lower() for word in regex_pattern.findall(text) if word.lower() not in STOPWORDS]

def compute_word_frequencies(tokens: list[Token]) -> dict[Token, int]:
    token_dict = {}
    for i in tokens:
        token_dict[i] = token_dict.get(i, 0) + 1
    return token_dict

def print_frequencies(frequencies: dict[Token, int]) -> None:
    sorted_dict = sorted(frequencies.items(), key=lambda item: item[1], reverse=True)
    for i, j in sorted_dict:
        print(f"{i} -> {j}")

def main():
    if len(sys.argv) != 2:
        print("Error: Wrong Argument")
        sys.exit(1)

    text = sys.argv[1]  # Accept raw text
    tokens = tokenize(text)
    token_dict = compute_word_frequencies(tokens)
    print_frequencies(token_dict)

if __name__ == "__main__":
    main()
