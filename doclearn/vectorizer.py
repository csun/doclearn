import re

import nltk
from nltk.corpus import wordnet

from sklearn.feature_extraction import DictVectorizer


def _getVerbInPhrase(phrase):
    tagged_tokens = nltk.pos_tag(nltk.word_tokenize(phrase))

    for token, tag in tagged_tokens:
        if tag[0] == 'V':
            return token

    return None


class Vectorizer(object):

    def __init__(self):
        self._features_template = {
            'verb_similarity': self._computeVerbSimilarity,
            'shared_keywords': self._computeSharedKeywords
        }
        self._measurements = []


    def _computeVerbSimilarity(self, code, documentation, phrase):
        # This makes a lot of assumptions about the structure of docs and code
        function_name = code.split('(')[0]
        function_documentation = documentation[function_name]

        function_verb = wordnet.synsets(
                _getVerbInPhrase(function_documentation))[0]
        phrase_verb = wordnet.synsets(_getVerbInPhrase(phrase))[0]

        similarity = function_verb.path_similarity(phrase_verb)
        if not similarity: similarity = 0

        return similarity

    def _computeSharedKeywords(self, code, documentation, phrase):
        # This is not a robust regex (and I don't fully understand it)
        code_keywords = re.split('[()_]', code)
        phrase_keywords = phrase.split()

        # This could also contain garbage like the empty string
        overlap = [el for el in code_keywords if el in phrase_keywords]
        return len(overlap)

    def addMeasurement(self, code, documentation, phrase):
        features_dict = {}
        for feature_name, feature_function in self._features_template.iteritems():
            features_dict[feature_name] = feature_function(
                    code, documentation, phrase)

        self._measurements.append(features_dict)

    def toArray(self):
        dict_vectorizer = DictVectorizer()
        return dict_vectorizer.fit_transform(self._measurements).toarray()
