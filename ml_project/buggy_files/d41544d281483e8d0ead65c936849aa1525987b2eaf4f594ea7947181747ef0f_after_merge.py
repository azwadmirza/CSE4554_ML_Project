    def update_tracker_info(self, tracker_url, is_successful):
        self.tribler_session.tracker_manager.update_tracker_info(tracker_url, is_successful)