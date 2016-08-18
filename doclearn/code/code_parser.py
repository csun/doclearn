import ast

from doclearn.node import Node


def _getOrDefaultToArray(dictionary, key):
    try:
        return dictionary[key]
    except KeyError:
        return []


def _getLabelAndRelatedTokensForLeaf(leaf):
    if isinstance(leaf, ast.Attribute):
        return (leaf.attr, _getTokensFromAttributeChain(leaf.value))
    elif isinstance(leaf, ast.Name):
        return (leaf.id, [])
    elif isinstance(leaf, ast.Str):
        return (leaf.s, [])
    elif isinstance(leaf, ast.Num):
        return (str(leaf.n), [])
    else:
        return (None, [])


def _getTokensFromAttributeChain(node):
    if isinstance(node, ast.Name):
        return [node.id]
    else:
        tokens = _getTokensFromAttributeChain(node.value)
        tokens.append(node.attr)
        return tokens


class _TreeVisitor(ast.NodeVisitor):
    def __init__(self):
        super(_TreeVisitor, self).__init__()

        self._current_parent_node = None
        self.line_root_nodes = {}


    def visit_Call(self, ast_node):
        label, related_tokens = _getLabelAndRelatedTokensForLeaf(ast_node.func)
        new_node = Node(label, Node.VERB_NODE, related_tokens=related_tokens)

        if self._current_parent_node is None:
            self.line_root_nodes[ast_node.lineno - 1] = new_node
        else:
            self._current_parent_node.addChild(new_node)

        prev_parent_node = self._current_parent_node
        self._current_parent_node = new_node

        for arg in ast_node.args:
            self._addChildIfArgIsLeaf(arg)

        self.generic_visit(ast_node)

        self._current_parent_node = prev_parent_node

    def _addChildIfArgIsLeaf(self, arg):
        label, related_tokens = _getLabelAndRelatedTokensForLeaf(arg)

        if label is None:
            return
        else:
            new_node = Node(label, Node.NOUN_NODE, related_tokens=related_tokens)
            self._current_parent_node.addChild(new_node)


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

        # TODO dictionary of line number to nodes? Should be in relevant visitor.

        self._documentation = {}
        if documentation:
            self._documentation = documentation

        self._visitor = _Visitor(self._documentation)
        self._tree_visitor = _TreeVisitor()
        self._visitor.visit(self._root_node)
        self._tree_visitor.visit(self._root_node)

    def getCalledFunctionNamesForLine(self, line):
        return _getOrDefaultToArray(self._visitor.line_function_names, line)

    def getArgumentNamesForLine(self, line):
        return _getOrDefaultToArray(self._visitor.line_argument_names, line)

    def getFunctionDocstringsForLine(self, line):
        return _getOrDefaultToArray(self._visitor.line_function_docstrings, line)

    def getRootNodeForLine(self, line):
        if line in self._tree_visitor.line_root_nodes:
            return self._tree_visitor.line_root_nodes[line]
        else:
            return None
