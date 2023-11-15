    def merge(self, ancestor_info, our_info, their_info):
        assert our_info
        assert their_info

        if ancestor_info:
            ancestor_hash = ancestor_info[self.tree.PARAM_CHECKSUM]
            ancestor = self.get_dir_cache(ancestor_hash)
        else:
            ancestor = []

        our_hash = our_info[self.tree.PARAM_CHECKSUM]
        our = self.get_dir_cache(our_hash)

        their_hash = their_info[self.tree.PARAM_CHECKSUM]
        their = self.get_dir_cache(their_hash)

        merged = self._merge_dirs(ancestor, our, their)
        hash_info = self.tree.save_dir_info(merged)
        return {hash_info.name: hash_info.value}