    def __contains__(self, path):
        # if already in inventory, always return True.
        return self.cache.in_inventory(path) or super().__contains__(path)