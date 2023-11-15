    def remove_node(self, node):
        for child in self.children[node.index + 1:]:
            child.index -= 1

        try:
            self.children.pop(node.index)
        except IndexError:
            pass
        for idx, next_idx in zip(self.children, self.children[1:]):
            assert idx.index < next_idx.index