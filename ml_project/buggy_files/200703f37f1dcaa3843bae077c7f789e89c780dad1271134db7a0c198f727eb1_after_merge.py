    def merge(self, ancestor_info, our_info, their_info):
        assert our_info
        assert their_info

        if ancestor_info:
            ancestor_hash = ancestor_info.value
            ancestor = self.get_dir_cache(ancestor_hash)
        else:
            ancestor = []

        our_hash = our_info.value
        our = self.get_dir_cache(our_hash)

        their_hash = their_info.value
        their = self.get_dir_cache(their_hash)

        merged = self._merge_dirs(ancestor, our, their)
        return self.tree.save_dir_info(merged)