    def add_torrent_def_to_channel(self, channel_id, torrent_def, extra_info=None, forward=True):
        """
        Adds a TorrentDef to a Channel.

        :param channel_id: id of the Channel to add the Torrent to
        :param torrent_def: definition of the Torrent to add
        :param extra_info: description of the Torrent to add
        :param forward: when True the messages are forwarded (as defined by their message
         destination policy) to other nodes in the community. This parameter should (almost always)
         be True, its inclusion is mostly to allow certain debugging scenarios
        """
        extra_info = extra_info or {}
        # Make sure that this new torrent_def is also in collected torrents
        self.lm.rtorrent_handler.save_torrent(torrent_def)

        channelcast_db = self.open_dbhandler(NTFY_CHANNELCAST)
        if channelcast_db.hasTorrent(channel_id, torrent_def.infohash):
            raise DuplicateTorrentFileError("This torrent file already exists in your channel.")

        dispersy_cid = str(channelcast_db.getDispersyCIDFromChannelId(channel_id))
        community = self.get_dispersy_instance().get_community(dispersy_cid)

        community._disp_create_torrent(
            torrent_def.infohash,
            cast_to_long(time.time()),
            torrent_def.get_name_as_unicode(),
            tuple(torrent_def.get_files_with_length()),
            torrent_def.get_trackers_as_single_tuple(),
            forward=forward)

        if 'description' in extra_info:
            desc = extra_info['description'].strip()
            if desc != '':
                data = channelcast_db.getTorrentFromChannelId(channel_id, torrent_def.infohash, ['ChannelTorrents.id'])
                community.modifyTorrent(data, {'description': desc}, forward=forward)