    def get_next_tracker_for_auto_check(self):
        """
        Gets the next tracker for automatic tracker-checking.
        :return: The next tracker for automatic tracker-checking.
        """
        tracker = self.tracker_store.select(lambda g: str(g.url)
                                            and g.alive
                                            and g.last_check + TRACKER_RETRY_INTERVAL <= int(time.time())
                                            and str(g.url) not in self.blacklist)\
            .order_by(self.tracker_store.last_check).limit(1)

        if not tracker:
            return None
        return tracker[0].url