    def _readFromUrl(cls, url, writable):
        srcBucket, srcKey = cls._extractKeyInfoFromUrl(url)
        srcKey.get_contents_to_file(writable)