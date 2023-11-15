    def on_credit_mining_sources(self, json_result):
        if not json_result:
            return
        if json_result["modified"]:
            old_source = next(iter(self.window().tribler_settings["credit_mining"]["sources"]), None)

            new_sources = [self.channel_info["dispersy_cid"]] if self.channel_info["dispersy_cid"] != old_source else []
            self.window().tribler_settings["credit_mining"]["sources"] = new_sources

            self.update_subscribe_button()

            channels_list = self.window().discovered_channels_list
            for index, data_item in enumerate(channels_list.data_items):
                if data_item[1]['dispersy_cid'] == old_source:
                    channel_item = channels_list.itemWidget(channels_list.item(index))
                    if channel_item:
                        channel_item.subscriptions_widget.update_subscribe_button()
                    break