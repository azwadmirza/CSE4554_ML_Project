    def exportFile(self, jobStoreFileID, dstUrl):
        """
        Exports file to destination pointed at by the destination URL.

        Refer to AbstractJobStore.importFile documentation for currently supported URL schemes.

        Note that the helper method _exportFile is used to read from the source and write to
        destination. To implement any optimizations that circumvent this, the _exportFile method
        should be overridden by subclasses of AbstractJobStore.

        :param str jobStoreFileID: The id of the file in the job store that should be exported.
        :param str dstUrl: URL that points to a file or object in the storage mechanism of a
                supported URL scheme e.g. a blob in an Azure Blob Storage container.
        """
        dstUrl = urlparse.urlparse(dstUrl)
        otherCls = self._findJobStoreForUrl(dstUrl, export=True)
        return self._exportFile(otherCls, jobStoreFileID, dstUrl)