    def _replace_prefix_in_path(self, old_prefix, new_prefix, starting_path_dirs=None):
        if starting_path_dirs is None:
            path_list = self._get_starting_path_list()
        else:
            path_list = list(starting_path_dirs)
        if on_win:  # pragma: unix no cover
            if old_prefix is not None:
                # windows has a nasty habit of adding extra Library\bin directories
                prefix_dirs = tuple(self._get_path_dirs(old_prefix))
                try:
                    first_idx = path_list.index(prefix_dirs[0])
                except ValueError:
                    first_idx = 0
                else:
                    last_idx = path_list.index(prefix_dirs[-1])
                    del path_list[first_idx:last_idx+1]
            else:
                first_idx = 0
            if new_prefix is not None:
                path_list[first_idx:first_idx] = list(self._get_path_dirs(new_prefix))
        else:
            if old_prefix is not None:
                try:
                    idx = path_list.index(join(old_prefix, 'bin'))
                except ValueError:
                    idx = 0
                else:
                    del path_list[idx]
            else:
                idx = 0
            if new_prefix is not None:
                path_list.insert(idx, join(new_prefix, 'bin'))
        return self.path_conversion(path_list)