    def stop_all_downloads(self):
        """
        Aborts all running downloads.
        """
        pyfiles = list(self.pyload.files.cache.values())
        for pyfile in pyfiles:
            pyfile.abort_download()