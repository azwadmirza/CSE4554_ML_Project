    def mtime_local(self):
        # do not follow symlinks for modification time
        if os.path.isdir(self.file) and os.path.exists(
            os.path.join(self.file, ".snakemake_timestamp")
        ):
            return os.lstat(os.path.join(self.file, ".snakemake_timestamp")).st_mtime
        else:
            return os.lstat(self.file).st_mtime