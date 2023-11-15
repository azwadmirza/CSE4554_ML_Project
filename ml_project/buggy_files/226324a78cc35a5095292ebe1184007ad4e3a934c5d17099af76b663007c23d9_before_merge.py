    def render_DELETE(self, request):
        """
        .. http:delete:: /channels/discovered/(string: channelid)/torrents/(string: torrent infohash)

        Remove a torrent with a given infohash from a given channel.

            **Example request**:

            .. sourcecode:: none

                curl -X DELETE http://localhost:8085/channels/discovered/abcdefg/torrents/
                97d2d8f5d37e56cfaeaae151d55f05b077074779

            **Example response**:

            .. sourcecode:: javascript

                {
                    "removed": True
                }

            :statuscode 404: if the channel is not found or if the torrent is not found in the specified channel
        """
        channel_info = self.get_channel_from_db(self.cid)
        if channel_info is None:
            return ChannelsTorrentsEndpoint.return_404(request)

        torrent_db_columns = ['Torrent.torrent_id', 'infohash', 'Torrent.name', 'length', 'Torrent.category',
                              'num_seeders', 'num_leechers', 'last_tracker_check', 'ChannelTorrents.dispersy_id']
        torrent_info = self.channel_db_handler.getTorrentFromChannelId(channel_info[0], self.path.decode('hex'),
                                                                       torrent_db_columns)

        if torrent_info is None:
            return BaseChannelsEndpoint.return_404(request, message=UNKNOWN_TORRENT_MSG)

        channel_community = self.get_community_for_channel_id(channel_info[0])
        if channel_community is None:
            return BaseChannelsEndpoint.return_404(request, message=UNKNOWN_COMMUNITY_MSG)

        channel_community.remove_torrents([torrent_info[8]])  # the 8th index is the dispersy id of the channel torrent

        return json.dumps({"removed": True})