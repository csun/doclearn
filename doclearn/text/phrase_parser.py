import spacy
from spacy import parts_of_speech
from spacy import symbols

from doclearn import constants
from doclearn.node import Node


def _generateNodeForToken(token, parent):
    if token.pos == parts_of_speech.VERB:
        node_type = Node.VERB_NODE
    else:
        node_type = Node.NOUN_NODE

    node = Node(token, node_type)
    unvisited = list(token.children)
    while unvisited:
        child = unvisited.pop()
        if (child.pos == parts_of_speech.VERB or
            child.dep in [symbols.nsubj, symbols.dobj, symbols.iobj, symbols.pobj, symbols.poss]):
            _generateNodeForToken(child, node)
        elif child.pos in [parts_of_speech.ADJ, parts_of_speech.ADV]:
            node.related_tokens.append(child)
        elif child.dep == symbols.conj:
            # NOTE if these things are joined by a conjunction, they should
            # be siblings
            _generateNodeForToken(child, parent)
        else:
            unvisited.extend(child.children)

    parent.addChild(node)


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

        root = self._doc[0]
        while root.head is not root:
            root = root.head
        self.tree = Node.createRootNode()
        _generateNodeForToken(root, self.tree)

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
