    def get_hash(self):
        if not self.use_cache:
            return self.tree.get_hash(self.path_info)
        return self.cache.get_hash(self.tree, self.path_info)