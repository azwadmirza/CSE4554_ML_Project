    def received_search_result_torrent(self, result):
        if self.is_duplicate_torrent(result):
            return
        torrent_index = min(bisect_right(result, self.search_results['torrents'], is_torrent=True),
                            len(self.search_results['torrents']))
        self.search_results['torrents'].insert(torrent_index, result)
        self.window().search_results_list.insert_item(
            torrent_index + len(self.search_results['channels']), (ChannelTorrentListItem, result))
        self.update_num_search_results()