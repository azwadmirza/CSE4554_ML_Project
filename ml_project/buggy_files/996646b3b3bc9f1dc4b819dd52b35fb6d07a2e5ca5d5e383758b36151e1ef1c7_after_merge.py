    def get_file_hash(self, path_info):
        outs = self._find_outs(path_info, strict=False)
        if len(outs) != 1:
            raise OutputNotFoundError
        out = outs[0]
        if out.is_dir_checksum:
            return HashInfo(
                out.tree.PARAM_CHECKSUM,
                self._get_granular_checksum(path_info, out),
            )
        return HashInfo(out.tree.PARAM_CHECKSUM, out.checksum)