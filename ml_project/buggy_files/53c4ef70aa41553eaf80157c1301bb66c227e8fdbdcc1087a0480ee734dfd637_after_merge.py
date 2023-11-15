    def commit(self):
        assert self.hash_info
        if self.use_cache:
            self.cache.save(
                self.path_info, self.cache.tree, self.hash_info.to_dict()
            )