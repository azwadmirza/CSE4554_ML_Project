    def _readFromUrl(cls, url, writable):
        blobService, containerName, blobName = cls._extractBlobInfoFromUrl(url)
        blobService.get_blob_to_file(containerName, blobName, writable)