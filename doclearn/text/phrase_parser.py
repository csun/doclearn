import spacy
from spacy import parts_of_speech
from spacy import symbols

from doclearn import constants


class PhraseParser(object):

    @classmethod
    def get_spacy(cls):
        if not hasattr(cls, '_loaded_spacy'):
            cls._loaded_spacy = spacy.load('en', via=constants.SPACY_DATA_DIR)
        return cls._loaded_spacy

    def __init__(self, phrase):
        nlp = PhraseParser.get_spacy()
        self._phrase = phrase
        self._doc = nlp(unicode(phrase))

        self._verbs = []
        self._objects = []

        self._processDoc()

    def _processDoc(self):
        for token in self._doc:
            token_string = str(token.string.lower().strip())

            if token.pos == parts_of_speech.VERB:
                self._verbs.append(token_string)
            elif token.dep in [symbols.dobj, symbols.iobj, symbols.pobj]:
                self._objects.append(token_string)

    def getVerbs(self):
        return self._verbs

    def getObjects(self):
        return self._objects
