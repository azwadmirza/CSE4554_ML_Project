    def get_next_tracker_for_auto_check(self):
        """
        Gets the next tracker for automatic tracker-checking.
        :return: The next tracker for automatic tracker-checking.
        """
        if len(self._tracker_dict) == 0:
            return

        next_tracker_url = None
        next_tracker_info = None

        sorted_tracker_list = sorted(self._tracker_dict.items(), key=lambda d: d[1][u'last_check'])

        for tracker_url, tracker_info in sorted_tracker_list:
            if tracker_url == u'DHT':
                next_tracker_url = tracker_url
                next_tracker_info = {u'is_alive': True, u'last_check': int(time.time())}
                break
            elif tracker_url != u'no-DHT' and self.should_check_tracker(tracker_url):
                next_tracker_url = tracker_url
                next_tracker_info = tracker_info
                break

        if next_tracker_url is None:
            return
        return next_tracker_url, next_tracker_info