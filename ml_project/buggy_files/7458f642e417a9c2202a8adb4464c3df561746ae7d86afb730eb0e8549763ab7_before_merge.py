    def needs_inventory(self, path):
        root = self.get_inventory_root(path)
        return root and root not in self.has_inventory