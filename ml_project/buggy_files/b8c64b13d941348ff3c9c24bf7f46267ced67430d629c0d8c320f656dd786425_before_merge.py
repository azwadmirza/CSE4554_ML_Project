    def update_subscribe_button(self, remote_response=None):
        if remote_response and "subscribed" in remote_response:
            self.contents_widget.model.channel_info["subscribed"] = remote_response["subscribed"]

        color = '#FE6D01' if int(self.contents_widget.model.channel_info["subscribed"]) else '#fff'
        self.subscribe_button.setStyleSheet('border:none; color: %s' % color)
        self.subscribe_button.setText(format_votes(self.contents_widget.model.channel_info['votes']))

        # Disable channel control buttons for LEGACY_ENTRY channels
        hide_controls = self.contents_widget.model.channel_info["status"] == 1000
        self.subscribe_button.setHidden(hide_controls)