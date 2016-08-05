import ast


class _Visitor(ast.NodeVisitor):

    def __init__(self):
        super(_Visitor, self).__init__()
        self.line_function_names = {}
        self.line_argument_names = {}

    def visit_Call(self, node):
        # NOTE ast starts line indices at 1, while we start at 0.
        # Decrement here to deal with that.
        lineno = node.lineno - 1

        self._addFunctionName(lineno, node.func)
        self._addFunctionArgs(lineno, node.args)
        self.generic_visit(node)

    def _addFunctionName(self, lineno, func):
        if lineno not in self.line_function_names: 
            self.line_function_names[lineno] = []

        function_name = self._getAttributeOrName(func)
        if function_name:
            self.line_function_names[lineno].append(function_name)

    def _addFunctionArgs(self, lineno, args):
        arg_names = []
        for arg in args:
            arg_name = self._getAttributeOrName(arg)

            if arg_name:
                arg_names.append(arg_name)

        if lineno not in self.line_argument_names: 
            self.line_argument_names[lineno] = []
        self.line_argument_names[lineno].extend(arg_names)

    def _getAttributeOrName(self, attr_or_name):
        if isinstance(attr_or_name, ast.Attribute):
            return attr_or_name.attr
        elif isinstance(attr_or_name, ast.Name):
            return attr_or_name.id
        else:
            return None


class CodeParser(object):

    def __init__(self, source_string):
        self._root_node = ast.parse(source_string)

        self._visitor = _Visitor()
        self._visitor.visit(self._root_node)

    def getCalledFunctionNamesForLine(self, line):
        try:
            return self._visitor.line_function_names[line]
        except KeyError:
            return []

    def getArgumentNamesForLine(self, line):
        try:
            return self._visitor.line_argument_names[line]
        except KeyError:
            return []
