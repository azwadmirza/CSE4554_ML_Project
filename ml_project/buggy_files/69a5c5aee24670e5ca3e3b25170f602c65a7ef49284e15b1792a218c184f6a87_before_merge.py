    def _importFile(self, otherCls, url, sharedFileName=None):
        """
        Import the file at the given URL using the given job store class to retrieve that file.
        See also :meth:`importFile`. This method applies a generic approach to importing: it asks
        the other job store class for a stream and writes that stream as eiher a regular or a
        shared file.

        :param AbstractJobStore  otherCls: The concrete subclass of AbstractJobStore that supports
               reading from the given URL.

        :param urlparse.ParseResult url: The location of the file to import.

        :param str sharedFileName: Optional name to assign to the imported file within the job store

        :return The jobStoreFileId of imported file or None if sharedFileName was given
        :rtype: str|None
        """
        if sharedFileName is None:
            with self.writeFileStream() as (writable, jobStoreFileID):
                otherCls._readFromUrl(url, writable)
                return jobStoreFileID
        else:
            self._requireValidSharedFileName(sharedFileName)
            with self.writeSharedFileStream(sharedFileName) as writable:
                otherCls._readFromUrl(url, writable)
                return None