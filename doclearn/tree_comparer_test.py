import unittest
from doclearn import tree_comparer
from doclearn.text import phrase_parser
from doclearn.code import code_parser


class TreeComparerTest(unittest.TestCase):

    def test_similar(self):
        phrase_tree = phrase_parser.PhraseParser('Returns the tax rate').tree
        code_tree = code_parser.CodeParser('return tax_rate').getRootNodeForLine(0)

        comparer = tree_comparer.TreeComparer(phrase_tree, code_tree)
        self.assertGreater(comparer.getParentChildStrongSimilarities(), .75)

    def test_not_similar(self):
        phrase_tree = phrase_parser.PhraseParser('Sets the failure mode').tree
        code_tree = code_parser.CodeParser('del tax_rate').getRootNodeForLine(0)

        comparer = tree_comparer.TreeComparer(phrase_tree, code_tree)
        self.assertEquals(comparer.getParentChildStrongSimilarities(), 0)
