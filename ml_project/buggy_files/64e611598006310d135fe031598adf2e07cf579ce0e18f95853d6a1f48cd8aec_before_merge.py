    def save_info(self, path_info, **kwargs):
        typ, hash_ = self.get_hash(path_info, **kwargs)
        return {typ: hash_}