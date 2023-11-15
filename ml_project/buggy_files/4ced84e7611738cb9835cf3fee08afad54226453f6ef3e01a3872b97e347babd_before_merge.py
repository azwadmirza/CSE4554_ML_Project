    def write_lockfile(self, content):
        """Write out the lockfile.
        """
        newlines = self._lockfile_newlines
        s = simplejson.dumps(  # Send Unicode in to guarentee Unicode out.
            content, indent=4, separators=(u",", u": "), sort_keys=True
        )
        with atomic_open_for_write(self.lockfile_location, newline=newlines) as f:
            f.write(s)
            if not s.endswith(u"\n"):
                f.write(u"\n")  # Write newline at end of document. GH #319.