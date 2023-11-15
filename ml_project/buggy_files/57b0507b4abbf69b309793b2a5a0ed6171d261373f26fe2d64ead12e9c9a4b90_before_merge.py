    def ignore(self, path, in_curr_dir=False):
        base_dir = (
            os.path.realpath(os.curdir)
            if in_curr_dir
            else os.path.dirname(path)
        )
        entry, gitignore = self._get_gitignore(path, base_dir)

        if self._ignored(entry, gitignore):
            return

        msg = "Adding '{}' to '{}'.".format(
            os.path.relpath(path), os.path.relpath(gitignore)
        )
        logger.info(msg)

        self._add_entry_to_gitignore(entry, gitignore)

        self.track_file(os.path.relpath(gitignore))

        self.ignored_paths.append(path)