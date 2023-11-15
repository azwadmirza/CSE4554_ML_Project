    def default_ep_status_name(self, status_name):
        """Set the default episode status using its name."""
        self.default_ep_status = next((status for status, name in iteritems(statusStrings)
                                       if name.lower() == status_name.lower()),
                                      self.default_ep_status)