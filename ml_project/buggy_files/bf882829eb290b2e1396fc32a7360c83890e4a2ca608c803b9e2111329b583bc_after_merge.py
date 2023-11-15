    def importFile(self, srcUrl, sharedFileName=None):
        """
        Imports the file at the given URL into job store. The ID of the newly imported file is
        returned. If the name of a shared file name is provided, the file will be imported as
        such and None is returned.

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
        # Note that the helper method _importFile is used to read from the source and write to
        # destination (which is the current job store in this case). To implement any
        # optimizations that circumvent this, the _importFile method should be overridden by
        # subclasses of AbstractJobStore.
        srcUrl = urlparse.urlparse(srcUrl)
        otherCls = self._findJobStoreForUrl(srcUrl)
        return self._importFile(otherCls, srcUrl, sharedFileName=sharedFileName)