    def spider_opened(self, spider):
        self.start_time = datetime.utcnow()
        self.stats.set_value('start_time', self.start_time, spider=spider)