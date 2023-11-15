    def on_cancel_health_check(self):
        """
        The request for torrent health could not be queued.
        Go back to the intial state.
        """
        self.health_text.setText("unknown health")
        self.set_health_indicator(STATUS_UNKNOWN)
        self.is_health_checking = False
        self.has_health = False