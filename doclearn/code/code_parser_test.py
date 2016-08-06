import unittest

from .code_parser import CodeParser

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
