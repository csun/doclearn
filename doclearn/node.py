class Node(object):

    ROOT_NODE = 'root_node'
    NOUN_NODE = 'noun_node'
    VERB_NODE = 'verb_node'

    @classmethod
    def createRootNode(cls):
        return cls(None, cls.ROOT_NODE)

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
