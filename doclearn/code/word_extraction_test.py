import unittest

from . import word_extraction


class WordExtractionTest(unittest.TestCase):

    def _assertCorrectWords(self, identifier, expected):
        words = word_extraction.identifier_to_words(identifier)
        self.assertEquals(words, expected)

    def test_single_word(self):
        self._assertCorrectWords('hello', ['hello'])

    def test_camel_case(self):
        self._assertCorrectWords('helloWorld', ['hello', 'world'])

    def test_pascal_case(self):
        self._assertCorrectWords('HelloWorld', ['hello', 'world'])

    def test_snake_case(self):
        self._assertCorrectWords('hello_world', ['hello', 'world'])

    def test_capital_snake_case(self):
        self._assertCorrectWords('HELLO_WORLD', ['hello', 'world'])

    def test_leading_underscore(self):
        self._assertCorrectWords('_hello_world', ['hello', 'world'])
