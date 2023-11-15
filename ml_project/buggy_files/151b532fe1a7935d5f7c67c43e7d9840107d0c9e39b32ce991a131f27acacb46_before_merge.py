    def get_file_hash(self, path_info):
        url = path_info.url

        headers = self._head(url).headers

        etag = headers.get("ETag") or headers.get("Content-MD5")

        if not etag:
            raise DvcException(
                "could not find an ETag or "
                "Content-MD5 header for '{url}'".format(url=url)
            )

        return self.PARAM_CHECKSUM, etag