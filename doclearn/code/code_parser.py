import ast


def _getOrDefaultToArray(dictionary, key):
    try:
        return dictionary[key]
    except KeyError:
        return []


class _Visitor(ast.NodeVisitor):

    def __init__(self, documentation):
        super(_Visitor, self).__init__()
        self._documentation = documentation

        self.line_function_names = {}
        self.line_argument_names = {}
        self.line_function_docstrings = {}

    def visit_Call(self, node):
        # NOTE ast starts line indices at 1, while we start at 0.
        # Decrement here to deal with that.
        lineno = node.lineno - 1
        self._initializeLineDataIfNoneExists(lineno)

        self._addFunctionName(lineno, node.func)
        self._addFunctionArgs(lineno, node.args)
        self._addFunctionDocstrings(lineno, node.func)
        self.generic_visit(node)

    def _initializeLineDataIfNoneExists(self, lineno):
        if lineno not in self.line_function_names:
            self.line_function_names[lineno] = []
            self.line_argument_names[lineno] = []
            self.line_function_docstrings[lineno] = []

    def _addFunctionName(self, lineno, func):
        function_name = self._getAttributeOrName(func)
        if function_name:
            self.line_function_names[lineno].append(function_name)

    def _addFunctionArgs(self, lineno, args):
        arg_names = []

        for arg in args:
            arg_name = self._getAttributeOrName(arg)
            if arg_name:
                arg_names.append(arg_name)

        self.line_argument_names[lineno].extend(arg_names)

    def _addFunctionDocstrings(self, lineno, func):
        def join_parts(existing, new):
            if existing:
                return new + '.' + existing
            else:
                return new

        complete_func_name = ''
        while func:
            if isinstance(func, ast.Name):
                complete_func_name = join_parts(complete_func_name, func.id)
                func = None
            elif isinstance(func, ast.Attribute):
                complete_func_name = join_parts(complete_func_name, func.attr)
                func = func.value
            else:
                return

            if complete_func_name in self._documentation:
                docstring = self._documentation[complete_func_name]
                self.line_function_docstrings[lineno].append(docstring)

    def _getAttributeOrName(self, attr_or_name):
        if isinstance(attr_or_name, ast.Attribute):
            return attr_or_name.attr
        elif isinstance(attr_or_name, ast.Name):
            return attr_or_name.id
        else:
            return None


class CodeParser(object):

    def __init__(self, source_string, documentation=None):
        self._root_node = ast.parse(source_string)

        self._documentation = {}
        if documentation:
            self._documentation = documentation

        self._visitor = _Visitor(self._documentation)
        self._visitor.visit(self._root_node)

    def getCalledFunctionNamesForLine(self, line):
        return _getOrDefaultToArray(self._visitor.line_function_names, line)

    def getArgumentNamesForLine(self, line):
        return _getOrDefaultToArray(self._visitor.line_argument_names, line)

    def getFunctionDocstringsForLine(self, line):
        return _getOrDefaultToArray(self._visitor.line_function_docstrings, line)
