    def received_subscribed_channels(self, results):
        self.window().subscribed_channels_list.set_data_items([])
        items = []

        if len(results['subscribed']) == 0:
            self.window().subscribed_channels_list.set_data_items(
                [(LoadingListItem, "You are not subscribed to any channel.")])
            return

        for result in results['subscribed']:
            items.append((ChannelListItem, result))
        self.window().subscribed_channels_list.set_data_items(items)