    def _readFromUrl(cls, url, writable):
        srcBucket, srcKey = cls._extractKeyInfoFromUrl(url, existing=True)
        srcKey.get_contents_to_file(writable)