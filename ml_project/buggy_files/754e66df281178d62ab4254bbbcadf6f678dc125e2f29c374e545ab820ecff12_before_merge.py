    def _update_params(self, params: dict):
        """Update experiment params files with the specified values."""
        from dvc.utils.serialize import MODIFIERS

        logger.debug("Using experiment params '%s'", params)

        # recursive dict update
        def _update(dict_, other):
            for key, value in other.items():
                if isinstance(value, Mapping):
                    dict_[key] = _update(dict_.get(key, {}), value)
                else:
                    dict_[key] = value
            return dict_

        for params_fname in params:
            path = PathInfo(self.exp_dvc.root_dir) / params_fname
            suffix = path.suffix.lower()
            modify_data = MODIFIERS[suffix]
            with modify_data(path, tree=self.exp_dvc.tree) as data:
                _update(data, params[params_fname])

        # Force params file changes to be staged in git
        # Otherwise in certain situations the changes to params file may be
        # ignored when we `git stash` them since mtime is used to determine
        # whether the file is dirty
        self.scm.add(list(params.keys()))