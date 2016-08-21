import ast

from doclearn.code.word_extraction import identifier_to_words
from doclearn.node import Node
from doclearn.text.phrase_parser import PhraseParser


def _getOrDefaultToArray(dictionary, key):
    try:
        return dictionary[key]
    except KeyError:
        return []


def _getLabelAndRelatedTokensForLeaf(leaf):
    if isinstance(leaf, ast.Attribute):
        attr_tokens = _getTokensFromAttributeChain(leaf.value)
        related_tokens = []
        for token in attr_tokens:
            related_tokens.extend(identifier_to_words(token))

        words = identifier_to_words(leaf.attr)
        related_tokens.extend(words[1:])
        return (words[0], related_tokens)
    elif isinstance(leaf, ast.Name):
        words = identifier_to_words(leaf.id)
        return (words[0], words[1:])
    elif isinstance(leaf, ast.Str):
        words = identifier_to_words(leaf.s)
        if not words:
            words = ['empty']
        return (words[0], words[1:])
    elif isinstance(leaf, ast.Num):
        return (str(leaf.n), [])
    elif isinstance(leaf, ast.Not):
        return ('not', ['opposite', 'inverse'])
    elif isinstance(leaf, ast.Add):
        return ('add', ['increase', 'plus'])
    elif isinstance(leaf, ast.Sub):
        return ('subtract', ['decrease', 'minus'])
    elif isinstance(leaf, ast.Mult):
        return ('multiply', ['times'])
    elif isinstance(leaf, ast.Div):
        return ('divide', [])
    elif isinstance(leaf, ast.Mod):
        return ('modulus', ['remainder'])
    elif isinstance(leaf, ast.And):
        return ('and', [])
    elif isinstance(leaf, ast.Or):
        return ('or', [])
    else:
        return (None, [])


def _getTokensFromAttributeChain(node):
    if isinstance(node, ast.Name):
        return [node.id]
    elif isinstance(node, ast.Attribute):
        tokens = _getTokensFromAttributeChain(node.value)
        tokens.append(node.attr)
        return tokens
    else:
        return []


class _TreeVisitor(ast.NodeVisitor):
    def __init__(self):
        super(_TreeVisitor, self).__init__()

        self._nlp = PhraseParser.get_spacy()
        self._current_parent_node = None
        self.line_root_nodes = {}

    def visit_Call(self, ast_node):
        self._processNodeWithLabelLeaf(ast_node.func, ast_node, ast_node.args)

    def visit_UnaryOp(self, ast_node):
        self._processOp(ast_node, [ast_node.operand])

    def visit_BinOp(self, ast_node):
        self._processOp(ast_node, [ast_node.left, ast_node.right])

    def visit_BoolOp(self, ast_node):
        self._processOp(ast_node, ast_node.values)

    def visit_Compare(self, ast_node):
        # NOTE This doesn't properly handle comparisons with multiple different
        # operators, but that's too much work.
        potential_leaves = ast_node.comparators[:]
        potential_leaves.append(ast_node.left)
        self._processNodeWithLabelLeaf(ast_node.ops[0], ast_node, potential_leaves)

    def visit_Subscript(self, ast_node):
        if isinstance(ast_node.slice, ast.Index):
            potential_leaves = [ast_node.slice.value]
        else:
            return

        self._processNodeWithLabelLeaf(ast_node.value, ast_node, potential_leaves,
                                       node_type = Node.NOUN_NODE)

    def visit_Assign(self, ast_node):
        potential_leaves = ast_node.targets
        potential_leaves.append(ast_node.value)
        self._processNode('set', ['assign'], Node.VERB_NODE, ast_node, potential_leaves)

    def visit_AugAssign(self, ast_node):
        if isinstance(ast_node.op, ast.Add):
            label, related_tokens = ('increment', ['increase'])
        elif isinstance(ast_node.op, ast.Sub):
            label, related_tokens = ('decrement', ['decrease'])
        else:
            label, related_tokens = ('set', ['assign'])

        self._processNode(label, related_tokens, Node.VERB_NODE, ast_node,
                          [ast_node.target, ast_node.value])

    def visit_Raise(self, ast_node):
        self._processNode('raise', ['throw'], Node.VERB_NODE, ast_node,
                          [ast_node.type])

    def visit_Delete(self, ast_node):
        self._processNode('delete', ['remove'], Node.VERB_NODE, ast_node,
                          ast_node.targets)

    def visit_Return(self, ast_node):
        self._processNode('return', [], Node.VERB_NODE, ast_node,
                          [ast_node.value])

    def _processOp(self, op_node, potential_leaves):
        self._processNodeWithLabelLeaf(op_node.op, op_node, potential_leaves)

    def _processNodeWithLabelLeaf(self, label_leaf, ast_node, potential_leaves, node_type=Node.VERB_NODE):
        label, related_tokens = _getLabelAndRelatedTokensForLeaf(label_leaf)

        if label is None:
            return

        self._processNode(label, related_tokens, node_type, ast_node, potential_leaves)

    def _processNode(self, label, related_tokens, node_type, ast_node, potential_leaves):
        label = self._nlp(unicode(label))[0]
        related_tokens = map(lambda x: self._nlp(unicode(x))[0], related_tokens)
        new_node = Node(label, node_type, related_tokens=related_tokens)

        if self._current_parent_node is None:
            self.line_root_nodes[ast_node.lineno - 1] = new_node
        else:
            self._current_parent_node.addChild(new_node)

        prev_parent_node = self._current_parent_node
        self._current_parent_node = new_node

        if potential_leaves:
            for potential in potential_leaves:
                self._addChildIfLeaf(potential)
        self.generic_visit(ast_node)

        self._current_parent_node = prev_parent_node

    def _addChildIfLeaf(self, node):
        label, related_tokens = _getLabelAndRelatedTokensForLeaf(node)

        if label is None:
            return
        else:
            label = self._nlp(unicode(label))[0]
            related_tokens = map(lambda x: self._nlp(unicode(x))[0], related_tokens)

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
