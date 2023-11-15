    def update_subscribe_button(self, remote_response=None):
        if remote_response and 'subscribed' in remote_response:
            self.channel_info["subscribed"] = remote_response['subscribed']

        if remote_response and 'votes' in remote_response:
            self.channel_info["votes"] = remote_response['votes']

        if self.channel_info["subscribed"]:
            self.subscribe_button.setIcon(QIcon(QPixmap(get_image_path('subscribed_yes.png'))))
        else:
            self.subscribe_button.setIcon(QIcon(QPixmap(get_image_path('subscribed_not.png'))))

        self.num_subs_label.setText(str(self.channel_info["votes"]))

        if self.window().tribler_settings:  # It could be that the settings are not loaded yet
            self.credit_mining_button.setHidden(not self.window().tribler_settings["credit_mining"]["enabled"])
            if self.channel_info["dispersy_cid"] in self.window().tribler_settings["credit_mining"]["sources"]:
                self.credit_mining_button.setIcon(QIcon(QPixmap(get_image_path('credit_mining_yes.png'))))
            else:
                self.credit_mining_button.setIcon(QIcon(QPixmap(get_image_path('credit_mining_not.png'))))
        else:
            self.credit_mining_button.hide()