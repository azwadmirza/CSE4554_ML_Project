    def start(self):
        """
        The Metadata Store checks the database at regular intervals to see if new channels are available for preview
        or subscribed channels require updating.
        """

        # Test if we our channel is there, but we don't share it because Tribler was closed unexpectedly
        try:
            with db_session:
                my_channel = self.session.lm.mds.ChannelMetadata.get_my_channel()
                if my_channel and my_channel.status == COMMITTED and \
                        not self.session.has_download(str(my_channel.infohash)):
                    torrent_path = os.path.join(self.session.lm.mds.channels_dir, my_channel.dir_name + ".torrent")
                    mdblob_path = os.path.join(self.session.lm.mds.channels_dir, my_channel.dir_name + ".mdblob")
                    tdef = None
                    if os.path.exists(torrent_path) and os.path.exists(mdblob_path):
                        try:
                            tdef = TorrentDef.load(torrent_path)
                        except IOError:
                            self._logger.warning("Can't open personal channel torrent file. Will try to regenerate it.")
                    tdef = tdef if (tdef and tdef.infohash != str(my_channel.infohash)) else\
                        TorrentDef.load_from_dict(my_channel.consolidate_channel_torrent())
                    self.updated_my_channel(tdef)
        except Exception:
            self._logger.exception("Error when tried to resume personal channel seeding on GigaChannel Manager startup")

        channels_check_interval = 5.0  # seconds
        self.channels_lc = self.register_task("Process channels download queue and remove cruft",
                                              LoopingCall(self.service_channels)).start(channels_check_interval)