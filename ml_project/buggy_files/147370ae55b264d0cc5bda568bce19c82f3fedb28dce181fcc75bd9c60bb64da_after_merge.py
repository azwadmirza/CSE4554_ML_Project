    def is_newer(self, time):
        """Returns true of the file is newer than time, or if it is
        a symlink that points to a file newer than time."""
        if self.is_ancient:
            return False
        elif self.is_remote:
            return self.mtime > time
        else:
            return self.mtime > time or self.mtime_target > time