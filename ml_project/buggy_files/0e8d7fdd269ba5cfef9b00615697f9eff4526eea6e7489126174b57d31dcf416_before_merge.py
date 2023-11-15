    def _writeToUrl(cls, readable, url):
        blobService, containerName, blobName = cls._extractBlobInfoFromUrl(url)
        blobService.put_block_blob_from_file(containerName, blobName, readable)
        blobService.get_blob(containerName, blobName)