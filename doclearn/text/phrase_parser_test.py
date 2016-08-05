import unittest

from .phrase_parser import PhraseParser


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
