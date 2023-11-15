    def _exportFile(self, otherCls, jobStoreFileID, url):
        """
        Refer to exportFile docstring for information about this method.

        :param AbstractJobStore otherCls: The concrete subclass of AbstractJobStore that supports
               exporting to the given URL. Note that the type annotation here is not completely
               accurate. This is not an instance, it's a class, but there is no way to reflect
               that in PEP-484 type hints.

        :param str jobStoreFileID: The id of the file that will be exported.

        :param urlparse.ParseResult url: The parsed URL of the file to export to.
        """
        with self.readFileStream(jobStoreFileID) as readable:
            otherCls._writeToUrl(readable, url)