    def mtime_local(self):
        # do not follow symlinks for modification time
        lstat = os.lstat(self.file)
        if stat.S_ISDIR(lstat.st_mode) and os.path.exists(
            os.path.join(self.file, TIMESTAMP_FILENAME)
        ):
            return os.lstat(os.path.join(self.file, TIMESTAMP_FILENAME)).st_mtime
        else:
            return lstat.st_mtime