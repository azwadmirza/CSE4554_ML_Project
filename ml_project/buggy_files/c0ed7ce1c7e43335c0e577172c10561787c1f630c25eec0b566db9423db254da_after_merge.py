    def __init__(self, name, node_type, parent):
        """
        Create a node for an import tree.

        :param name: Name of the node.
        :type name: str
        :param node_type: Type of the node.
        :type node_type: NodeType
        :param parent: Parent node of this node.
        :type parent: Node
        """

        self.name = name
        self.node_type = node_type
        self.parent = parent

        if not self.parent and self.node_type is not NodeType.ROOT:
            raise Exception("Only node with type ROOT are allowed to have no parent")

        self.depth = 0
        if self.node_type is NodeType.ROOT:
            self.depth = 0

        else:
            self.depth = self.parent.depth + 1

        self.children = {}

        self.marked = False
        self.alias = ""