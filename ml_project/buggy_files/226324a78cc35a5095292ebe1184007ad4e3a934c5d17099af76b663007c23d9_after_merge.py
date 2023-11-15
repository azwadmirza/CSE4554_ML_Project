    def render_DELETE(self, request):
        """
        .. http:delete:: /channels/discovered/(string: channelid)/torrents/(string: comma separated torrent infohashes)

        Remove a single or multiple torrents with the given comma separated infohashes from a given channel.

            **Example request**:

            .. sourcecode:: none

                curl -X DELETE http://localhost:8085/channels/discovered/abcdefg/torrents/
                97d2d8f5d37e56cfaeaae151d55f05b077074779,971d55f05b077074779d2d8f5d37e56cfaeaae15

            **Example response**:

            .. sourcecode:: javascript

                {
                    "removed": True
                }

            .. sourcecode:: javascript

                {
                    "removed": False, "failed_torrents":["97d2d8f5d37e56cfaeaae151d55f05b077074779"]
                }

            :statuscode 404: if the channel is not found
        """
        channel_info = self.get_channel_from_db(self.cid)
        if channel_info is None:
            return ChannelsTorrentsEndpoint.return_404(request)

        channel_community = self.get_community_for_channel_id(channel_info[0])
        if channel_community is None:
            return BaseChannelsEndpoint.return_404(request, message=UNKNOWN_COMMUNITY_MSG)

        torrent_db_columns = ['Torrent.torrent_id', 'infohash', 'Torrent.name', 'length', 'Torrent.category',
                              'num_seeders', 'num_leechers', 'last_tracker_check', 'ChannelTorrents.dispersy_id']

        failed_torrents = []
        for torrent_path in self.path.split(","):
            torrent_info = self.channel_db_handler.getTorrentFromChannelId(channel_info[0],
                                                                           torrent_path.decode('hex'),
                                                                           torrent_db_columns)
            if torrent_info is None:
                failed_torrents.append(torrent_path)
            else:
                # the 8th index is the dispersy id of the channel torrent
                channel_community.remove_torrents([torrent_info[8]])

        if failed_torrents:
            return json.dumps({"removed": False, "failed_torrents": failed_torrents})

        return json.dumps({"removed": True})