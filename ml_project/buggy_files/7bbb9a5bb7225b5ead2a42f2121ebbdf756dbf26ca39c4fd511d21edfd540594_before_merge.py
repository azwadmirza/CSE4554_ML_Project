    def path2doc(self, filename):
        # type: (unicode) -> Optional[unicode]
        """Return the docname for the filename if the file is document.

        *filename* should be absolute or relative to the source directory.
        """
        if filename.startswith(self.srcdir):
            filename = os.path.relpath(filename, self.srcdir)
        for suffix in self.config.source_suffix:
            if filename.endswith(suffix):
                return filename[:-len(suffix)]
        return None