    def in_inventory(self, path):
        root = self.get_inventory_root(path)
        return root and root in self.has_inventory