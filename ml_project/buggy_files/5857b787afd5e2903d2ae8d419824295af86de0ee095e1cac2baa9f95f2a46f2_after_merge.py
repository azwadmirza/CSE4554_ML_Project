    def _set_fileview_root(self, path, *, tabbed=False):
        """Set the root path for the file display."""
        separators = os.sep
        if os.altsep is not None:
            separators += os.altsep

        dirname = os.path.dirname(path)
        basename = os.path.basename(path)
        if not tabbed:
            self._to_complete = ''

        try:
            if not path:
                pass
            elif path in separators and os.path.isdir(path):
                # Input "/" -> don't strip anything
                pass
            elif path[-1] in separators and os.path.isdir(path):
                # Input like /foo/bar/ -> show /foo/bar/ contents
                path = path.rstrip(separators)
            elif os.path.isdir(dirname) and not tabbed:
                # Input like /foo/ba -> show /foo contents
                path = dirname
                self._to_complete = basename
            else:
                return
        except OSError:
            log.prompt.exception("Failed to get directory information")
            return

        root = self._file_model.setRootPath(path)
        self._file_view.setRootIndex(root)