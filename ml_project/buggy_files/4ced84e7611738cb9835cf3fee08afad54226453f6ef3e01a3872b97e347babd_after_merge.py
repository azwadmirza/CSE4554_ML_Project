    def write_lockfile(self, content):
        """Write out the lockfile.
        """
        s = self._lockfile_encoder.encode(content)
        open_kwargs = {
            'newline': self._lockfile_newlines,
            'encoding': 'utf-8',
        }
        with atomic_open_for_write(self.lockfile_location, **open_kwargs) as f:
            f.write(s)
            # Write newline at end of document. GH-319.
            # Only need '\n' here; the file object handles the rest.
            if not s.endswith(u"\n"):
                f.write(u"\n")