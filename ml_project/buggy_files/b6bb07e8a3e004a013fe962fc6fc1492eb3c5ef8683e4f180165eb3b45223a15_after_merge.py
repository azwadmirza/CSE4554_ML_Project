    def received_search_result_channel(self, result):
        # Ignore channels that have a small amount of torrents or have no votes
        if result['torrents'] <= 2 or result['votes'] == 0:
            return
        if self.is_duplicate_channel(result):
            return
        channel_index = min(bisect_right(result, self.search_results['channels'], is_torrent=False),
                            len(self.search_results['channels']))
        self.window().search_results_list.insert_item(channel_index, (ChannelListItem, result))
        self.search_results['channels'].insert(channel_index, result)
        self.update_num_search_results()