    def spider_closed(self, spider, reason):
        finish_time = datetime.datetime.utcnow()
        elapsed_time = finish_time - self.stats.get_value('start_time')
        elapsed_time_seconds = elapsed_time.total_seconds()
        self.stats.set_value('elapsed_time_seconds', elapsed_time_seconds, spider=spider)
        self.stats.set_value('finish_time', finish_time, spider=spider)
        self.stats.set_value('finish_reason', reason, spider=spider)