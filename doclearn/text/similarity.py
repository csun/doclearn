from nltk.corpus import wordnet


def word_similarity(word1, word2):
    """
    Return the similarity between two lists of words.

    The result of this function will either be None (if no similarity found) or
    a float between 0 and 1.

    If either word has multiple meanings, the meaning that leads to the highest
    similarity will be used.

    May not work well for verbs because the wordnet function used is targeted
    more towards nouns.
    """
    synset1 = wordnet.synsets(word1)
    synset2 = wordnet.synsets(word2)

    if not synset1 and synset2:
        return None

    current_best = None
    for s1 in synset1:
        for s2 in synset2:
            similarity = wordnet.path_similarity(s1, s2)
            if (not current_best and similarity) or (similarity > current_best):
                current_best = similarity

    return current_best
