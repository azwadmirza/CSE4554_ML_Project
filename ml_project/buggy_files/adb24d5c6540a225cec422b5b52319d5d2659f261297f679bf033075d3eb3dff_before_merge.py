    def _get_dir_info_hash(self, dir_info):
        # Sorting the list by path to ensure reproducibility
        dir_info = sorted(dir_info, key=itemgetter(self.PARAM_RELPATH))

        tmp = tempfile.NamedTemporaryFile(delete=False).name
        with open(tmp, "w+") as fobj:
            json.dump(dir_info, fobj, sort_keys=True)

        tree = self.cache.tree
        from_info = PathInfo(tmp)
        to_info = tree.path_info / tmp_fname("")
        tree.upload(from_info, to_info, no_progress_bar=True)

        typ, hash_ = tree.get_file_hash(to_info)
        return typ, hash_ + self.CHECKSUM_DIR_SUFFIX, to_info