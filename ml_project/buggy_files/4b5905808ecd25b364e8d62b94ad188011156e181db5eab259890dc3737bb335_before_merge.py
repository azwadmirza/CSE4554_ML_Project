    def _download_and_hash(self, urls):
        """
        Downloads the file and returns the path, hash and url it used to download.

        Parameters
        ----------
        urls: `list`
            List of urls.

        Returns
        -------
        `str`, `str`, `str`
            Path, hash and URL of the file.
        """
        def download(url):
            path = self._cache_dir / get_filename(urlopen(url), url)
            path = replacement_filename(path)
            self._downloader.download(url, path)
            shahash = hash_file(path)
            return path, shahash, url

        for url in urls:
            try:
                return download(url)
            except Exception as e:
                warn(e, SunpyUserWarning)
        else:
            raise RuntimeError("Download failed")