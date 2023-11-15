    def copy(self, node_cache=None):
        if node_cache and self.name in node_cache:
            return node_cache[self.name]

        s = Node(self.name, self.data)
        for c in self.children:
            c = c.copy(node_cache=node_cache)
            s.add_child(c)
        return s