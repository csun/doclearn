import ast


class _FunctionNameLister(ast.NodeVisitor):

    def __init__(self):
        super(_FunctionNameLister, self).__init__()
        self.line_function_names = {}

    def visit_Call(self, node):
        if node.lineno not in self.line_function_names:
            self.line_function_names[node.lineno] = []

        if isinstance(node.func, ast.Attribute):
            function_name = node.func.attr
        elif isinstance(node.func, ast.Name):
            function_name = node.func.id
        else:
            self.generic_visit(node)
            return

        self.line_function_names[node.lineno].append(function_name)
        self.generic_visit(node)


class CodeParser(object):

    def __init__(self, source_string):
        self._root_node = ast.parse(source_string)

        self._function_name_lister = _FunctionNameLister()
        self._function_name_lister.visit(self._root_node)

    def getCalledFunctionNamesForLine(self, line):
        # NOTE ast starts line indices at 1, while we start at 0.
        # Increment here to deal with that.
        try:
            return self._function_name_lister.line_function_names[line + 1]
        except KeyError:
            return []
