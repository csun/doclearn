from sklearn.feature_extraction import DictVectorizer


class Vectorizer(object):

    def __init__(self, description, documentation, snippet_lines):
        self._description = description
        self._documentation = documentation
        self._snippet_lines = snippet_lines

        self._features_template = {
            # 'verb_similarity': self._computeVerbSimilarity,
            'shared_keywords': self._computeSharedKeywords
        }

    def generateVectorsForDescriptionSubstring(self, start, end):
        all_vectors = []

        shortened_phrase = self._description[start:end]
        for line in self._snippet_lines:
            all_vectors.append(self._createVector(
                line, self._documentation, shortened_phrase))

        dict_vectorizer = DictVectorizer()
        return dict_vectorizer.fit_transform(all_vectors).toarray()

    def _createVector(self, code, documentation, phrase):
        features_dict = {}
        for feature_name, feature_function in self._features_template.iteritems():
            features_dict[feature_name] = feature_function(
                    code, documentation, phrase)

        return features_dict

    # TODO make this actually work and add back in
    def _computeVerbSimilarity(self, code, documentation, phrase):
        # This makes a lot of assumptions about the structure of docs and code
        try:
            function_name = code.split('(')[0]
            function_documentation = documentation[function_name]

            function_verb = wordnet.synsets(
                    _getVerbInPhrase(function_documentation))[0]
            phrase_verb = wordnet.synsets(_getVerbInPhrase(phrase))[0]

            similarity = function_verb.path_similarity(phrase_verb)
            if not similarity: similarity = 0

            return similarity
        except:
            return 0

    def _computeSharedKeywords(self, code, documentation, phrase):
        # This is not a robust regex (and I don't fully understand it)
        code_keywords = re.split('[()_, ]', code)
        phrase_keywords = phrase.split()

        # This could also contain garbage like the empty string
        overlap = [el for el in code_keywords if el in phrase_keywords]
        return len(overlap)
