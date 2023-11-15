    def received_torrents_in_channel(self, results):
        if not results:
            return
        def sort_key(torrent):
            """ Scoring algorithm for sorting the torrent to show liveness. The score is basically the sum of number
                of seeders and leechers. If swarm info is unknown, we give unknown seeder and leecher as 0.5 & 0.4 so
                that the sum is less than 1 and higher than zero. This means unknown torrents will have higher score
                than dead torrent with no seeders and leechers and lower score than any barely alive torrent with a
                single seeder or leecher.
            """
            seeder_score = torrent['num_seeders'] if torrent['num_seeders'] or torrent['last_tracker_check'] > 0\
                else 0.5
            leecher_score = torrent['num_leechers'] if torrent['num_leechers'] or torrent['last_tracker_check'] > 0\
                else 0.5
            return seeder_score + .5 * leecher_score

        for result in sorted(results['torrents'], key=sort_key, reverse=True):
            self.torrents.append((ChannelTorrentListItem, result))

        if not self.channel_info['subscribed']:
            self.torrents.append((TextListItem, "You're looking at a preview of this channel.\n"
                                                "Subscribe to this channel to see the full content."))

        self.loaded_channels = True
        self.update_result_list()