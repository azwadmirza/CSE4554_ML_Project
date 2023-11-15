        def download(url):
            path = self._cache_dir / get_filename(urlopen(url), url)
            path = replacement_filename(path)
            self._downloader.download(url, path)
            shahash = hash_file(path)
            return path, shahash, url