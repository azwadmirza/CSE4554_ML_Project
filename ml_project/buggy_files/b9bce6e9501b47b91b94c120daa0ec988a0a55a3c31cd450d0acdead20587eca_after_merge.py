    def _collect_dir(self, path_info, **kwargs):
        file_infos = set()

        for fname in self.walk_files(path_info, **kwargs):
            if DvcIgnore.DVCIGNORE_FILE == fname.name:
                raise DvcIgnoreInCollectedDirError(fname.parent)

            file_infos.add(fname)

        hashes = {fi: self.state.get(fi) for fi in file_infos}
        not_in_state = {fi for fi, hash_ in hashes.items() if hash_ is None}

        new_hashes = self._calculate_hashes(not_in_state)
        hashes.update(new_hashes)

        return [
            {
                self.PARAM_CHECKSUM: hashes[fi],
                # NOTE: this is lossy transformation:
                #   "hey\there" -> "hey/there"
                #   "hey/there" -> "hey/there"
                # The latter is fine filename on Windows, which
                # will transform to dir/file on back transform.
                #
                # Yes, this is a BUG, as long as we permit "/" in
                # filenames on Windows and "\" on Unix
                self.PARAM_RELPATH: fi.relative_to(path_info).as_posix(),
            }
            for fi in file_infos
        ]