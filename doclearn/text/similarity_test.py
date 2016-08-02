import unittest

from . import similarity


class SimilarityTest(unittest.TestCase):

    def test_similar_words(self):
        self.assertGreater(similarity.max_word_similarity('cat', 'dog'), 0)

    def test_non_similar_words(self):
        self.assertEquals(similarity.max_word_similarity('dastardly', 'kitten'), None)

    def test_nonexistent_words(self):
        self.assertEquals(similarity.max_word_similarity('asd', 'bqp'), None)
