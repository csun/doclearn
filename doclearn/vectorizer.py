import re

from sklearn.feature_extraction import DictVectorizer

from .code import code_parser, word_extraction
from .text import phrase_parser, similarity

class Vectorizer(object):

    def __init__(self, description, documentation, snippet_lines):
        self._description = description
        self._documentation = documentation
        self._snippet_lines = snippet_lines

        self._code_parser = code_parser.CodeParser(''.join(snippet_lines))

        self._current_line_number = 0
        self._current_line = ''
        self._current_phrase_start = 0
        self._current_phrase_end = 0
        self._current_phrase = ''
        self._current_phrase_parser = None

    def generateVectorsForDescriptionSubstring(self, start, end):
        all_feature_dicts = []

        self._current_phrase_start = start
        self._current_phrase_end = end
        self._current_phrase = self._description[start:end]
        self._current_phrase_parser = phrase_parser.PhraseParser(
                self._current_phrase)

        for line_number in range(len(self._snippet_lines)):
            self._current_line_number = line_number
            self._current_line = self._snippet_lines[line_number]
            all_feature_dicts.append(self._generateVector())

        dict_vectorizer = DictVectorizer()
        return dict_vectorizer.fit_transform(all_feature_dicts).toarray()

    def _generateVector(self):
        features_dict = {}

        features_dict['verb_function_similarity'] = (
                self._computeVerbFunctionSimilarity())
        features_dict['object_argument_similarity'] = (
                self._computeObjectArgumentSimilarity())
        features_dict['naive_shared_keywords'] = (
                self._naiveComputeSharedKeywords())

        return features_dict

    # ==========================================================================
    # === FEATURES =============================================================
    # ==========================================================================
    def _computeVerbFunctionSimilarity(self):
        called_functions = self._code_parser.getCalledFunctionNamesForLine(
                self._current_line_number)
        phrase_verbs = self._current_phrase_parser.getVerbs()

        return self._getMaxSimilarityBetweenIdentifiersAndWords(
                called_functions, phrase_verbs)

    def _computeObjectArgumentSimilarity(self):
        argument_names = self._code_parser.getArgumentNamesForLine(
                self._current_line_number)
        phrase_objects = self._current_phrase_parser.getObjects()

        return self._getMaxSimilarityBetweenIdentifiersAndWords(
                argument_names, phrase_objects)

    def _naiveComputeSharedKeywords(self):
        # This is not a robust regex (and I don't fully understand it)
        code_keywords = re.split('[()_, ]', self._current_line)
        phrase_keywords = self._current_phrase.split()

        # This could also contain garbage like the empty string
        overlap = [el for el in code_keywords if el in phrase_keywords]
        return len(overlap)

    # ==========================================================================
    # === HELPERS ==============================================================
    # ==========================================================================
    def _getMaxSimilarityBetweenIdentifiersAndWords(self, identifiers, words):
        identifier_words = []
        for identifier in identifiers:
            identifier_words.extend(
                    word_extraction.identifier_to_words(identifier))

        max_similarity = 0
        for identifier_word in identifier_words:
            for phrase_word in words:
                current_similarity = similarity.max_word_similarity(
                        identifier_word, phrase_word)
                if current_similarity and current_similarity > max_similarity:
                    max_similarity = current_similarity

        return max_similarity
