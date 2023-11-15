    def importFile(self, srcUrl, sharedFileName=None):
        """
        Imports the file at the given URL into job store. The jobStoreFileId of the new
        file is returned. If a shared file name is given, the file will be imported as a shared
        file and None is returned.

        Note that the helper method _importFile is used to read from the source and write to
        destination (which is the current job store in this case). To implement any optimizations that
        circumvent this, the _importFile method should be overridden by subclasses of AbstractJobStore.

        Currently supported schemes are:
            - 's3' for objects in Amazon S3
                e.g. s3://bucket/key

            - 'wasb' for blobs in Azure Blob Storage
                e.g. wasb://container/blob

            - 'file' for local files
                e.g. file:///local/file/path

            - 'http'
                e.g. http://someurl.com/path

        :param str srcUrl: URL that points to a file or object in the storage mechanism of a
                supported URL scheme e.g. a blob in an Azure Blob Storage container.

        :param str sharedFileName: Optional name to assign to the imported file within the job store

        :return The jobStoreFileId of the imported file or None if sharedFileName was given
        :rtype: str|None
        """
        url = urlparse.urlparse(srcUrl)
        otherCls = findJobStoreForUrl(url)
        return self._importFile(otherCls, url, sharedFileName=sharedFileName)