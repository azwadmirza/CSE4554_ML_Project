    def _exportFile(self, otherCls, jobStoreFileID, url):
        """
        Refer to exportFile docstring for information about this method.

        :param type otherCls: The concrete subclass of AbstractJobStore that supports exporting to the given URL.
        :param str jobStoreFileID: The id of the file that will be exported.
        :param urlparse.ParseResult url: The parsed url given to importFile.
        """
        with self.readFileStream(jobStoreFileID) as readable:
            otherCls._writeToUrl(readable, url)