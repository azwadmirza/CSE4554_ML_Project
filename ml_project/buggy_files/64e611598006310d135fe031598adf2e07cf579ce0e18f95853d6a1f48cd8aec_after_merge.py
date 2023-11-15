    def save_info(self, path_info, **kwargs):
        hash_info = self.get_hash(path_info, **kwargs)
        return {hash_info.name: hash_info.value}