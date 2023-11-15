    def _get_gitignore(self, path, ignore_file_dir=None):
        if not ignore_file_dir:
            ignore_file_dir = os.path.dirname(os.path.realpath(path))

        assert os.path.isabs(path)
        assert os.path.isabs(ignore_file_dir)

        if not path.startswith(ignore_file_dir):
            msg = (
                "{} file has to be located in one of '{}' subdirectories"
                ", not outside '{}'"
            )
            raise FileNotInTargetSubdirError(
                msg.format(self.GITIGNORE, path, ignore_file_dir)
            )

        entry = os.path.relpath(path, ignore_file_dir).replace(os.sep, "/")
        # NOTE: using '/' prefix to make path unambiguous
        if len(entry) > 0 and entry[0] != "/":
            entry = "/" + entry

        gitignore = os.path.join(ignore_file_dir, self.GITIGNORE)

        if not gitignore.startswith(os.path.realpath(self.root_dir)):
            raise FileNotInRepoError(path)

        return entry, gitignore