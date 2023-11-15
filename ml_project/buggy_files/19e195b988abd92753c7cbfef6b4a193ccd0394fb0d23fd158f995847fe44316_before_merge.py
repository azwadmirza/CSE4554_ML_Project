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

        def on_channel_download_finished(dl):
            channel_dirname = os.path.join(self.session.lm.mds.channels_dir, dl.get_def().get_name())
            self.session.lm.mds.process_channel_dir(channel_dirname, channel.public_key, channel.id_,
                                                    external_thread=True)
            self.session.lm.mds._db.disconnect()

        def _on_failure(failure):
            self._logger.error("Error when processing channel dir download: %s", failure)

        def _on_success(_):
            with db_session:
                channel_upd = self.session.lm.mds.ChannelMetadata.get(public_key=channel.public_key, id_=channel.id_)
                channel_upd_dict = channel_upd.to_simple_dict()
            self.session.notifier.notify(NTFY_CHANNEL_ENTITY, NTFY_UPDATE,
                                         "%s:%s".format(hexlify(channel.public_key), str(channel.id_)),
                                         channel_upd_dict)

        finished_deferred = download.finished_deferred.addCallback(
            lambda dl: deferToThread(on_channel_download_finished, dl))
        finished_deferred.addCallbacks(_on_success, _on_failure)

        return download, finished_deferred