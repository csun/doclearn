class Node(object):

    NOUN_NODE = 'noun_node'
    VERB_NODE = 'verb_node'

    def __init__(self, label, node_type, related_tokens=None):
        self.parent = None

        self.label = label
        self.node_type = node_type
        self.children = []

        self.related_tokens = []
        if related_tokens:
            self.related_tokens = related_tokens

    def addChild(self, child):
        child.parent = self
        self.children.append(child)
