import re

from sklearn.feature_extraction import DictVectorizer

from . import utils
from .code import code_parser
from .text import phrase_parser


class Vectorizer(object):

    def __init__(self, description, documentation, snippet_lines):
        self._description = description
        self._documentation = documentation
        self._snippet_lines = snippet_lines

        self._code_parser = code_parser.CodeParser(''.join(snippet_lines))

        self._current_features_dict = {}
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
            self._generateFeaturesDict()
            all_feature_dicts.append(self._current_features_dict)

        dict_vectorizer = DictVectorizer()
        return dict_vectorizer.fit_transform(all_feature_dicts).toarray()

    def _generateFeaturesDict(self):
        self._current_features_dict = {}

        self._computeVerbFunctionSimilarity()
        self._computeObjectArgumentSimilarity()
        self._computeFunctionDocstringSimilarity()
        self._naiveComputeSharedKeywords()

    # ==========================================================================
    # === FEATURES =============================================================
    # ==========================================================================
    def _computeVerbFunctionSimilarity(self):
        called_functions = self._code_parser.getCalledFunctionNamesForLine(
                self._current_line_number)
        phrase_verbs = self._current_phrase_parser.getVerbs()

        similarity = utils.identifier_and_word_max_similarity(
                called_functions, phrase_verbs)
        self._current_features_dict['verb_function_similarity'] = similarity

    def _computeObjectArgumentSimilarity(self):
        argument_names = self._code_parser.getArgumentNamesForLine(
                self._current_line_number)
        phrase_objects = self._current_phrase_parser.getObjects()

        similarity = utils.identifier_and_word_max_similarity(
                argument_names, phrase_objects)
        self._current_features_dict['object_arguments_similarity'] = similarity

    def _computeFunctionDocstringSimilarity(self):
        joined_docstrings = '\n'.join(
                self._code_parser.getFunctionDocstringsForLine(
                    self._current_line_number))
        docstring_parser = phrase_parser.PhraseParser(joined_docstrings)

        docstring_verbs = docstring_parser.getVerbs()
        docstring_objects = docstring_parser.getObjects()
        phrase_verbs = self._current_phrase_parser.getVerbs()
        phrase_objects = self._current_phrase_parser.getObjects()

        self._current_features_dict['verb_docstring_similarity'] = (
                utils.word_max_similarity(docstring_verbs, phrase_verbs))
        self._current_features_dict['object_docstring_similarity'] = (
                utils.word_max_similarity(docstring_objects, phrase_objects))

    def _naiveComputeSharedKeywords(self):
        # This is not a robust regex (and I don't fully understand it)
        code_keywords = re.split('[()_, ]', self._current_line)
        phrase_keywords = self._current_phrase.split()

        # This could also contain garbage like the empty string
        overlap = [el for el in code_keywords if el in phrase_keywords]
        self._current_features_dict['naive_shared_keywords'] = len(overlap)
