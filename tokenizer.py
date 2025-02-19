import sys
import os
import re

Token = str
def tokenize(file_path: str) -> list[Token]:
    try:
        file_size = os.path.getsize(file_path)
        threshold = 100 * 1024 * 1024
        tokens = []

        # Open file safely with error handling for encoding issues
        with open(file_path, 'r', encoding = 'utf-8', errors = 'ignore') as file:
            if file_size < threshold:
                text = file.read()
                text = re.sub(r'[^\w]', ' ',
                              text.lower())
                tokens = re.findall(r'\w+',
                                    text)
            else:
                for line in file:
                    line = re.sub(r'[^\w]', ' ', line.lower())
                    tokens.extend(re.findall(r'\w+', line))

        return tokens
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return []
    except Exception as e:
        print(f"Error: An unexpected issue occurred while processing '{file_path}': {e}")
        return []


def compute_word_frequencies(tokens: list[Token]) -> dict[Token, int]:
    frequencies = {}
    for token in tokens:
        frequencies[token] = frequencies.get(token, 0) + 1
    return frequencies


def print_frequencies(frequencies: dict[Token, int]) -> None:
    sorted_tokens = sorted(frequencies.items(), key = lambda item: (-item[1], item[0]))
    for token, freq in sorted_tokens:
        print(f"{token} -> {freq}")


def main():
    if len(sys.argv) != 2:
        print("Usage: python tokenizer.py <text_file>")
        sys.exit(1)

    file_path = sys.argv[1]
    tokens = tokenize(file_path)
    if tokens:
        token_frequencies = compute_word_frequencies(tokens)
        print_frequencies(token_frequencies)
    else:
        print("No tokens found in the file.")


if __name__ == "__main__":
    main()
