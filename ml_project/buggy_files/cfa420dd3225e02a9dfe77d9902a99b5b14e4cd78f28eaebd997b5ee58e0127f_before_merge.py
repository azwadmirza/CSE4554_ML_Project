    def readStatsAndLogging(self, statsCallBackFn):
        itemsProcessed = 0
        items = None
        for attempt in retry_sdb():
            with attempt:
                items = list(self.filesDomain.select(
                    consistent_read=True,
                    query="select * from `%s` where ownerID='%s'" % (
                        self.filesDomain.name, str(self.statsFileOwnerID))))
        assert items is not None
        for item in items:
            info = self.FileInfo.fromItem(item)
            with info.downloadStream() as readable:
                statsCallBackFn(readable)
            self.deleteFile(item.name)
            itemsProcessed += 1
        return itemsProcessed