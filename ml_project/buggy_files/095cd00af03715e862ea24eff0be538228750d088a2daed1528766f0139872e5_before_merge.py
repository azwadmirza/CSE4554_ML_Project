    def _update_params(self, params: dict):
        """Update experiment params files with the specified values."""
        from benedict import benedict

        from dvc.utils.serialize import MODIFIERS

        logger.debug("Using experiment params '%s'", params)

        for params_fname in params:
            path = PathInfo(self.repo.root_dir) / params_fname
            suffix = path.suffix.lower()
            modify_data = MODIFIERS[suffix]
            with modify_data(path, tree=self.repo.tree) as data:
                benedict(data).merge(params[params_fname], overwrite=True)

        # Force params file changes to be staged in git
        # Otherwise in certain situations the changes to params file may be
        # ignored when we `git stash` them since mtime is used to determine
        # whether the file is dirty
        self.scm.add(list(params.keys()))