    def spider_closed(self, spider, reason):
        if self.task and self.task.running:
            self.task.stop()