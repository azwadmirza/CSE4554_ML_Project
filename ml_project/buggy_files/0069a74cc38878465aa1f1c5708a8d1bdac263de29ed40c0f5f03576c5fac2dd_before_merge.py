    def on_channel_unsubscribed(self, json_result):
        if json_result["unsubscribed"]:
            self.unsubscribed_channel.emit(self.channel_info)
            self.channel_info["subscribed"] = False
            self.channel_info["votes"] -= 1
            self.update_subscribe_button()