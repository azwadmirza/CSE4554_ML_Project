    def received_discovered_channels(self, results):
        if not results or 'channels' not in results:
            return

        self.discovered_channels = []
        self.window().discovered_channels_list.set_data_items([])
        items = []

        results['channels'].sort(key=lambda x: x['torrents'], reverse=True)

        for result in results['channels']:
            items.append((ChannelListItem, result))
            self.discovered_channels.append(result)
            self.update_num_label()
        self.window().discovered_channels_list.set_data_items(items)