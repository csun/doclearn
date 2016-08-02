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
