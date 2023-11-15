    def try_filesize(self):
        try:
            return os.path.getsize(syspath(self.path))
        except (OSError, Exception) as exc:
            log.warning(u'could not get filesize: {0}', exc)
            return 0