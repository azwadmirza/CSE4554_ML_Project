    def on_channel_subscribed(self, json_result):
        if not json_result:
            return
        if json_result["subscribed"]:
            self.subscribed_channel.emit(self.channel_info)
            self.channel_info["subscribed"] = True
            self.channel_info["votes"] += 1
            self.update_subscribe_button()