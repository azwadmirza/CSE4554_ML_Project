    def get_dir_hash(self, path_info, **kwargs):
        try:
            outs = self._find_outs(path_info, strict=True)
            if len(outs) == 1 and outs[0].is_dir_checksum:
                out = outs[0]
                # other code expects us to fetch the dir at this point
                self._fetch_dir(out, **kwargs)
                return HashInfo(out.tree.PARAM_CHECKSUM, out.checksum)
        except OutputNotFoundError:
            pass

        return super().get_dir_hash(path_info, **kwargs)