import unittest

from .vectorizer import Vectorizer

class VectorizerTest(unittest.TestCase):

    def test_works(self):
        description = 'hello world'
        documentation = {'fn': 'Does something.'}
        snippet_lines = ['a = fn()\n', 'b += fn(a)']

        vectorizer = Vectorizer(description, documentation, snippet_lines)
        vectors = vectorizer.generateVectorsForDescriptionSubstring(0, 5)

        self.assertEqual(len(vectors), len(snippet_lines))
