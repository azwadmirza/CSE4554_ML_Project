    def _writeToUrl(cls, readable, url):
        blob = cls._parseWasbUrl(url)
        blob.service.put_block_blob_from_file(container_name=blob.container,
                                              blob_name=blob.name,
                                              stream=readable)