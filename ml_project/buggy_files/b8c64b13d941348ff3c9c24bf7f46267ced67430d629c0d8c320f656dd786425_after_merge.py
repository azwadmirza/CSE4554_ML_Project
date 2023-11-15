    def update_subscribe_button(self, remote_response=None):
        # A safeguard against race condition that happens when the user changed
        # the channel view before the response came in
        if self.isHidden():
            return
        if remote_response and "subscribed" in remote_response:
            self.contents_widget.model.channel_info["subscribed"] = remote_response["subscribed"]

        color = '#FE6D01' if int(self.contents_widget.model.channel_info["subscribed"]) else '#fff'
        self.subscribe_button.setStyleSheet('border:none; color: %s' % color)
        self.subscribe_button.setText(format_votes(self.contents_widget.model.channel_info['votes']))