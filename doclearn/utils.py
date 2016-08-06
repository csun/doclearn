from .code import word_extraction
from .text import similarity


def identifier_and_word_max_similarity(identifiers, words):
    identifier_words = []
    for identifier in identifiers:
        identifier_words.extend(
                word_extraction.identifier_to_words(identifier))

    return word_max_similarity(identifier_words, words)


def word_max_similarity(words1, words2):
    current_max = 0

    for word1 in words1:
        for word2 in words2:
            current = similarity.word_similarity(word1, word2)
            if current and current > current_max:
                current_max = current

    return current_max

