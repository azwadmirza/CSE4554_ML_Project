    def async_download(self, stop_request=None):
        headers = requests.utils.default_headers()
        headers["User-Agent"] = "Lutris/%s" % __version__
        if self.referer:
            headers["Referer"] = self.referer
        response = requests.get(self.url, headers=headers, stream=True)
        self.full_size = int(response.headers.get("Content-Length", "").strip() or 0)
        for chunk in response.iter_content(chunk_size=1024 * 1024):
            if not self.file_pointer:
                break
            if chunk:
                self.downloaded_size += len(chunk)
                self.file_pointer.write(chunk)