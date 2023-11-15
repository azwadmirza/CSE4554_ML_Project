    def try_filesize(self):
        """Get the size of the underlying file in bytes.

        If the file is missing, return 0 (and log a warning).
        """
        try:
            return os.path.getsize(syspath(self.path))
        except (OSError, Exception) as exc:
            log.warning(u'could not get filesize: {0}', exc)
            return 0