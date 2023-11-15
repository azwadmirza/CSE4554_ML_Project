    def _readFromUrl(cls, url, writable):
        blob = cls._parseWasbUrl(url)
        blob.service.get_blob_to_file(container_name=blob.container,
                                      blob_name=blob.name,
                                      stream=writable)