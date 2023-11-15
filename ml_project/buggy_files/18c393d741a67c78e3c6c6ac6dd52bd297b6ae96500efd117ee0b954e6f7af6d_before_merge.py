    def _importFile(self, otherCls, url):
        if issubclass(otherCls, AWSJobStore):
            srcBucket, srcKey = self._extractKeyInfoFromUrl(url)
            info = self.FileInfo.create(srcKey.name)
            info.copyFrom(srcKey)
            info.save()
            return info.fileID
        else:
            return super(AWSJobStore, self)._importFile(otherCls, url)