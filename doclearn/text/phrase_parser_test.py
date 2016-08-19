import unittest

from .phrase_parser import PhraseParser
from doclearn.node import Node


class PhraseParserTest(unittest.TestCase):

    def test_single_verb_extraction(self):
        parser = PhraseParser('The quick brown dog jumps over the lazy fox.')

        verbs = parser.getVerbs()
        self.assertEquals('jumps', verbs[0])

    def test_multiple_verb_extraction(self):
        parser = PhraseParser('The cat barks and whines loudly.')

        verbs = parser.getVerbs()
        self.assertEquals(['barks', 'whines'], verbs)

    def test_single_direct_object_extraction(self):
        parser = PhraseParser('The cat bites people.')

        objects = parser.getObjects()
        self.assertEquals(['people'], objects)

    def test_multiple_object_extraction(self):
        parser = PhraseParser('Then, the cat sends flowers to people.')

        objects = parser.getObjects()
        self.assertEquals(['flowers', 'people'], objects)


class PhraseParserTreeTest(unittest.TestCase):
    # TODO test ability to handle things like random funciton name

    def _assertTokenMatchesString(self, token, string):
        self.assertEquals(token.lower_, string.lower())

    def test_simple_phrase(self):
        parser = PhraseParser('Quickly returns the sum.')

        root = parser.tree.children[0]
        self._assertTokenMatchesString(root.label, 'returns')
        self._assertTokenMatchesString(root.related_tokens[0], 'quickly')
        self.assertEquals(root.node_type, Node.VERB_NODE)

        self.assertEquals(len(root.children), 1)
        child = root.children[0]
        self._assertTokenMatchesString(child.label, 'sum')
        self.assertEquals(child.node_type, Node.NOUN_NODE)

    def test_conjunction(self):
        parser = PhraseParser('Quickly returns the sum and the dog.')

        root = parser.tree.children[0]
        self.assertEquals(len(root.children), 2)

        for child in root.children:
            self.assertTrue(child.label.lower_ in ['sum', 'dog'])

    def test_possessive(self):
        parser = PhraseParser('Quickly returns the son\'s smelly dog.')

        root = parser.tree.children[0]
        self.assertEquals(len(root.children), 1)

        child = root.children[0]
        self._assertTokenMatchesString(child.label, 'dog')
        self._assertTokenMatchesString(child.related_tokens[0], 'smelly')
        self.assertEquals(len(child.children), 1)

        grandchild = child.children[0]
        self._assertTokenMatchesString(grandchild.label, 'son')

    def test_handles_function_names(self):
        parser = PhraseParser('Quickly returns somefn.')

        root = parser.tree.children[0]
        child = root.children[0]
        self._assertTokenMatchesString(child.label, 'somefn')
