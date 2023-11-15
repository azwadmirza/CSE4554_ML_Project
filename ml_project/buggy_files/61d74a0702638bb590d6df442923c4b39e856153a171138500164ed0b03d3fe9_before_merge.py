    def merge(self, ancestor_info, our_info, their_info):
        assert our_info
        assert their_info

        if ancestor_info:
            ancestor = self.get_dir_cache(ancestor_info)
        else:
            ancestor = []

        our = self.get_dir_cache(our_info)
        their = self.get_dir_cache(their_info)

        merged = self._merge_dirs(ancestor, our, their)
        return self.tree.save_dir_info(merged)