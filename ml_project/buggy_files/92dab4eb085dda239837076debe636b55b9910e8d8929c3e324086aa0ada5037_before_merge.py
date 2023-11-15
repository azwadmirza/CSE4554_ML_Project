    def copy(self):
        s = Node(self.name, self.data)
        for c in self.children:
            c = c.copy()
            s.add_child(c)
        return s