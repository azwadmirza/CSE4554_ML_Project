    def update_tracker_info(self, tracker_url, value):
        self.tribler_session.tracker_manager.update_tracker_info(tracker_url, value)