import unittest

from .code_parser import CodeParser
from doclearn.node import Node

class CodeParserFunctionNamesTest(unittest.TestCase):

    def test_single_line(self):
        parser = CodeParser('fn()')

        function_names = parser.getCalledFunctionNamesForLine(0)
        self.assertEquals('fn', function_names[0])

    def test_nonexistent_line(self):
        parser = CodeParser('fn()')

        function_names = parser.getCalledFunctionNamesForLine(100)
        self.assertEquals([], function_names)

    def test_call_of_a_call(self):
        parser = CodeParser('fn()()')

        function_names = parser.getCalledFunctionNamesForLine(0)
        self.assertEquals('fn', function_names[0])

    def test_attribute_function(self):
        parser = CodeParser('abc.asd.fn()')

        function_names = parser.getCalledFunctionNamesForLine(0)
        self.assertEquals('fn', function_names[0])

    def test_nested_function(self):
        parser = CodeParser('fn(fn2())')

        function_names = parser.getCalledFunctionNamesForLine(0)
        self.assertIn('fn', function_names)
        self.assertIn('fn2', function_names)

    def test_multiple_lines(self):
        parser = CodeParser('fn()\nfn2()')

        function_names = parser.getCalledFunctionNamesForLine(0)
        self.assertEquals('fn', function_names[0])

        function_names = parser.getCalledFunctionNamesForLine(1)
        self.assertEquals('fn2', function_names[0])

    def test_multiline_function(self):
        parser = CodeParser('fn(\n'
                            '        a)\n'
                            'fn2()')

        function_names = parser.getCalledFunctionNamesForLine(0)
        self.assertEquals('fn', function_names[0])

        function_names = parser.getCalledFunctionNamesForLine(2)
        self.assertEquals('fn2', function_names[0])

    def test_nested_multiline_function(self):
        parser = CodeParser('fn(\n'
                            '        fn2())')

        function_names = parser.getCalledFunctionNamesForLine(0)
        self.assertEquals('fn', function_names[0])

        function_names = parser.getCalledFunctionNamesForLine(1)
        self.assertEquals('fn2', function_names[0])


class CodeParserArgumentNamesTest(unittest.TestCase):

    def test_single_arg(self):
        parser = CodeParser('fn(a)')

        function_names = parser.getArgumentNamesForLine(0)
        self.assertEquals('a', function_names[0])

    def test_multiple_args(self):
        parser = CodeParser('fn(a, b)')

        function_names = parser.getArgumentNamesForLine(0)
        self.assertIn('a', function_names)
        self.assertIn('b', function_names)

    def test_nested_args(self):
        parser = CodeParser('fn(a, fn2(b))')

        function_names = parser.getArgumentNamesForLine(0)
        self.assertIn('a', function_names)
        self.assertIn('b', function_names)


class CodeParserDocumentationTest(unittest.TestCase):

    def test_single_function(self):
        parser = CodeParser('fn()', documentation={'fn': 'A function'})

        documentation = parser.getFunctionDocstringsForLine(0)
        self.assertEquals(['A function'], documentation)

    def test_multiple_functions(self):
        parser = CodeParser(
                'fn(fn2())',
                documentation={'fn': 'A function', 'fn2': 'Another'})

        documentation = parser.getFunctionDocstringsForLine(0)
        self.assertEquals(['A function', 'Another'], documentation)

    def test_attribute_functions(self):
        parser = CodeParser(
                'a.b.fn(c.d.fn2())',
                documentation={'a.b.fn': 'A function', 'd.fn2': 'Another'})

        documentation = parser.getFunctionDocstringsForLine(0)
        self.assertEquals(['A function', 'Another'], documentation)

    def test_nonexistent_docstring(self):
        parser = CodeParser('a.b.fn()')

        documentation = parser.getFunctionDocstringsForLine(0)
        self.assertEquals([], documentation)


class CodeParserTreeTest(unittest.TestCase):

    def test_simple_function_parse(self):
        parser = CodeParser('a.b.fn()')
        node = parser.getRootNodeForLine(0)
        self.assertEquals(node.label.lower_, 'fn')

        for token in node.related_tokens:
            self.assertTrue(token.lower_ == 'a' or token.lower_ == 'b')

        self.assertEquals(node.node_type, Node.VERB_NODE)
        self.assertEquals(node.children, [])

    def test_function_args_parse(self):
        parser = CodeParser('fn("a", b)')
        node = parser.getRootNodeForLine(0)
        self.assertEquals(len(node.children), 2)

        for child in node.children:
            self.assertTrue(child.label.lower_ == 'a' or child.label.lower_ == 'b')
            self.assertEquals(child.node_type, Node.NOUN_NODE)

    def test_nested_function_parse(self):
        parser = CodeParser('fn(fn2())')
        node = parser.getRootNodeForLine(0)

        self.assertEquals(len(node.children), 1)
        self.assertEquals(node.children[0].node_type, Node.VERB_NODE)
        self.assertEquals(node.children[0].label.lower_, 'fn2')

    def test_parse_with_comment(self):
        parser = CodeParser('# hi\na.b.fn()')
        self.assertEquals(parser.getRootNodeForLine(0), None)
        self.assertNotEquals(parser.getRootNodeForLine(1), None)

    def test_return_call(self):
        parser = CodeParser('return fn()')

        node = parser.getRootNodeForLine(0)
        self.assertEquals(node.label.lower_, 'return')
        self.assertEquals(node.node_type, Node.VERB_NODE)

        fn_node = node.children[0]
        self.assertEquals(fn_node.label.lower_, 'fn')

    def test_return_identifier(self):
        parser = CodeParser('return a.b')

        node = parser.getRootNodeForLine(0)
        child_node = node.children[0]
        self.assertEquals(child_node.label.lower_, 'b')

    def test_nested_op(self):
        parser = CodeParser('fn(a + b)')

        node = parser.getRootNodeForLine(0)
        add_node = node.children[0]
        self.assertEquals(add_node.label.lower_, 'add')
        self.assertEquals(len(add_node.children), 2)

        for child in add_node.children:
            self.assertTrue(child.label.lower_ == 'a' or child.label.lower_ == 'b')
            self.assertEquals(child.node_type, Node.NOUN_NODE)

    def test_subscript(self):
        parser = CodeParser('a.b[c]')

        node = parser.getRootNodeForLine(0)
        self.assertEquals(node.label.lower_, 'b')
        self.assertEquals(node.related_tokens[0].lower_, 'a')
        self.assertEquals(node.node_type, Node.NOUN_NODE)

        self.assertEquals(node.children[0].label.lower_, 'c')
        self.assertEquals(node.children[0].node_type, Node.NOUN_NODE)
