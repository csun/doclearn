import unittest

from .phrase_parser import PhraseParser


class PhraseParserTest(unittest.TestCase):

    def test_single_verb(self):
        parser = PhraseParser('The quick brown dog jumps over the lazy fox.')

        verbs = parser.getVerbs()
        self.assertEquals('jumps', verbs[0])
