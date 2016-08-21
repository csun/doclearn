from doclearn.node import Node


def _convert_tree(tree, parent=None):
    if parent is None:
        node_id = 'root'
    else:
        node_id = parent.node_id + '.' + str(len(parent.children))

    compare_node = _CompareNode(node_id, tree)
    if parent is not None:
        parent.addChild(compare_node)

    for child in tree.children:
        _convert_tree(child, parent=compare_node)

    return compare_node


def _get_all_nodes(node):
    matches = [node]

    for child in node.children:
        matches.extend(_get_all_nodes(child))

    return matches


def _get_max_node_similarity(n1, n2):
    n1_tokens = n1.related_tokens[:]
    n1_tokens.append(n1.label)
    n2_tokens = n2.related_tokens[:]
    n2_tokens.append(n2.label)

    current_max = 0
    for t1 in n1_tokens:
        for t2 in n2_tokens:
            if t1 and t2:
                similarity = t1.similarity(t2)
                if similarity > current_max:
                    current_max = similarity

    return current_max


STRONG_SIMILARITY_THRESHOLD = 0.2
def _has_strong_child_similarity(node):
    for similarity, other_node in node.similar_nodes:
        if similarity > STRONG_SIMILARITY_THRESHOLD:
            for child in other_node.children:
                for child_similarity, child_other in child.similar_nodes:
                    if (child_similarity > STRONG_SIMILARITY_THRESHOLD and
                        child_other.node_id.startswith(node.node_id)):
                        return True

    return False

def _has_strong_child_parent_similarity(node):
    for similarity, other_node in node.similar_nodes:
        if similarity > STRONG_SIMILARITY_THRESHOLD:
            if not other_node.parent:
                return False

            for parent_sim, parent_other in other_node.parent.similar_nodes:
                if (parent_sim > STRONG_SIMILARITY_THRESHOLD and
                    parent_other.node_id.startswith(node.node_id)):
                    return True

    return False

def _has_strong_grandchild_similarity(node):
    for similarity, other_node in node.similar_nodes:
        if similarity > STRONG_SIMILARITY_THRESHOLD:
            for child in other_node.children:
                for gchild in child.children:
                    for gchild_similarity, gchild_other in gchild.similar_nodes:
                        if (gchild_similarity > STRONG_SIMILARITY_THRESHOLD and
                            gchild_other.node_id.startswith(node.node_id)):
                            return True

    return False


class _CompareNode(object):

    def __init__(self, node_id, original_node):
        self.node_id = node_id
        self.node_type = original_node.node_type
        self.label = original_node.label
        self.related_tokens = original_node.related_tokens

        self.parent = None
        self.similar_nodes = []
        self.children = []
        self.grandchildren = []

    def addChild(self, child):
        child.parent = self
        self.children.append(child)
        if self.parent:
            self.parent.grandchildren.append(child)


class TreeComparer(object):

    def __init__(self, phrase_tree, code_tree):
        self._converted_phrase_tree = _convert_tree(phrase_tree)
        self._converted_code_tree = _convert_tree(code_tree)
        self._code_nodes = _get_all_nodes(self._converted_code_tree)

        self.total_phrase_parents = 0

        self._generateSimilarities()

    def _generateSimilarities(self):
        unvisited = [self._converted_phrase_tree]

        while unvisited:
            node = unvisited.pop()
            unvisited.extend(node.children)
            if node.node_type == Node.ROOT_NODE:
                continue

            if node.children:
                self.total_phrase_parents += 1

            targets = self._code_nodes

            for target in targets:
                similarity = _get_max_node_similarity(node, target)
                node.similar_nodes.append((similarity, target))
                target.similar_nodes.append((similarity, node))

    def getParentChildStrongSimilarities(self):
        if self.total_phrase_parents == 0:
            return 0

        unvisited = [self._converted_phrase_tree]

        found = 0.0
        while unvisited:
            node = unvisited.pop()
            if _has_strong_child_similarity(node):
                found += 1
            unvisited.extend(node.children)

        return found / self.total_phrase_parents

    def getAllSimilarityCounts(self):
        unvisited = [self._converted_phrase_tree]

        found_child = 0
        found_parent = 0
        found_grandchild = 0

        while unvisited:
            node = unvisited.pop()
            if _has_strong_child_similarity(node):
                found_child += 1
            if _has_strong_child_parent_similarity(node):
                found_parent += 1
            if _has_strong_grandchild_similarity(node):
                found_grandchild += 1

            unvisited.extend(node.children)

        return (found_child, found_parent, found_grandchild)
