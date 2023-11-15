    def commit(self):
        assert self.info
        if self.use_cache:
            self.cache.save(self.path_info, self.cache.tree, self.info)