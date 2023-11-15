    def get_valid_next_tracker_for_auto_check(self):
        tracker_url = self.get_next_tracker_for_auto_check()
        while tracker_url and not is_valid_url(tracker_url):
            self.remove_tracker(tracker_url)
            tracker_url = self.get_next_tracker_for_auto_check()
        return tracker_url