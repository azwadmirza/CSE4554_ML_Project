    def already_cached(self, path_info):
        assert path_info.scheme in ["", "local"]

        typ, current_md5 = self.tree.get_hash(path_info)

        assert typ == "md5"

        if not current_md5:
            return False

        return not self.changed_cache(current_md5)