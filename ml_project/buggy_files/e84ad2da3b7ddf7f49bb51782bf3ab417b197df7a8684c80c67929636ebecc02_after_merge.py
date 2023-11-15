    def already_cached(self, path_info):
        assert path_info.scheme in ["", "local"]

        current = self.tree.get_hash(path_info)

        assert current.name == "md5"

        if not current:
            return False

        return not self.changed_cache(current.value)