    def _task_scrape(self):
        deferred = self.parse_feed()

        if not self._to_stop:
            # schedule the next scraping task
            self._logger.info(u"Finish scraping %s, schedule task after %s", self.rss_url, self.check_interval)
            self.register_task(u'rss_scrape',
                               reactor.callLater(self.check_interval, self._task_scrape))

        return deferred