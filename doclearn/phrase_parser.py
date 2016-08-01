import nltk


class PhraseParser(object):

    def __init__(self, phrase):
        self._phrase = phrase
        self._token_tag_pairs = nltk.pos_tag(nltk.word_tokenize(phrase))

    def getVerbs(self):
        verbs = []

        for token, tag in self._token_tag_pairs:
            if tag[0] == 'V':
                verbs.append(token)

        return verbs
