    def get_valid_next_tracker_for_auto_check(self):
        tracker = self.get_next_tracker_for_auto_check()
        while tracker and not is_valid_url(tracker.url):
            self.remove_tracker(tracker.url)
            tracker = self.get_next_tracker_for_auto_check()
        return tracker