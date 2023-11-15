    def download_channel(self, channel):
        """
        Download a channel with a given infohash and title.
        :param channel: The channel metadata ORM object.
        """
        dcfg = DownloadStartupConfig(state_dir=self.session.config.get_state_dir())
        dcfg.set_dest_dir(self.session.lm.mds.channels_dir)
        dcfg.set_channel_download(True)
        tdef = TorrentDefNoMetainfo(infohash=str(channel.infohash), name=channel.dir_name)
        download = self.session.start_download_from_tdef(tdef, dcfg)

        def _add_channel_to_processing_queue(_):
            self.channels_processing_queue.append(channel)

        finished_deferred = download.finished_deferred.addCallback(_add_channel_to_processing_queue)

        return download, finished_deferred