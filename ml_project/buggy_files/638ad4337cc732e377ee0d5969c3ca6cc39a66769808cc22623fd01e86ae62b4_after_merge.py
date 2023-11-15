    def get_files_number(self, filter_info=None):
        from funcy import ilen

        if not self.use_cache or not self.hash_info:
            return 0

        if not self.hash_info.isdir:
            return 1

        if not filter_info or filter_info == self.path_info:
            return self.hash_info.nfiles or 0

        if not self.hash_info.dir_info:
            return 0

        return ilen(
            filter_info.isin_or_eq(self.path_info.joinpath(*relpath))
            for relpath, _ in self.hash_info.dir_info.items()
        )