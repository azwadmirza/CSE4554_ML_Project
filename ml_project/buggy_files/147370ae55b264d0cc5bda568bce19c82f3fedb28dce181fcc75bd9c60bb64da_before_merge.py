    def is_newer(self, time):
        """Returns true of the file is newer than time, or if it is
        a symlink that points to a file newer than time."""
        if self.is_ancient:
            return False
        elif self.is_remote:
            # If file is remote but provider does not override the implementation this
            # is the best we can do.
            return self.mtime > time
        else:
            if os.path.isdir(self.file) and os.path.exists(
                os.path.join(self.file, ".snakemake_timestamp")
            ):
                st_mtime_file = os.path.join(self.file, ".snakemake_timestamp")
            else:
                st_mtime_file = self.file
            try:
                return os.stat(st_mtime_file).st_mtime > time or self.mtime > time
            except FileNotFoundError:
                raise WorkflowError(
                    "File {} not found although it existed before. Is there another active process that might have deleted it?".format(
                        self.file
                    )
                )