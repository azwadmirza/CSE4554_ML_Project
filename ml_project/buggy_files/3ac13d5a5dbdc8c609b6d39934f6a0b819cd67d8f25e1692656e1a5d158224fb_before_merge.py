    def get_file_hash(self, path_info):
        # Use webdav client info method to get etag
        etag = self._client.info(path_info.path)["etag"].strip('"')

        # From HTTPTree
        if not etag:
            raise DvcException(
                "could not find an ETag or "
                "Content-MD5 header for '{url}'".format(url=path_info.url)
            )

        return self.PARAM_CHECKSUM, etag