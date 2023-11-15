    def render_PUT(self, request):
        """
        .. http:put:: /channels/discovered/(string: channelid)/torrents/http%3A%2F%2Ftest.com%2Ftest.torrent

        Add a torrent by magnet or url to your channel. Returns error 500 if something is wrong with the torrent file
        and DuplicateTorrentFileError if already added to your channel (except with magnet links).

            **Example request**:

            .. sourcecode:: none

                curl -X PUT http://localhost:8085/channels/discovered/abcdefg/torrents/
                http%3A%2F%2Ftest.com%2Ftest.torrent --data "description=nice video"

            **Example response**:

            .. sourcecode:: javascript

                {
                    "added": "http://test.com/test.torrent"
                }

            :statuscode 404: if your channel does not exist.
            :statuscode 500: if the specified torrent is already in your channel.
        """
        channel = self.get_channel_from_db(self.cid)
        if channel is None:
            return BaseChannelsEndpoint.return_404(request)

        parameters = http.parse_qs(request.content.read(), 1)

        if 'description' not in parameters or len(parameters['description']) == 0:
            extra_info = {}
        else:
            extra_info = {'description': parameters['description'][0]}

        def _on_url_fetched(data):
            return TorrentDef.load_from_memory(data)

        def _on_magnet_fetched(meta_info):
            return TorrentDef.load_from_dict(meta_info)

        def _on_torrent_def_loaded(torrent_def):
            self.session.add_torrent_def_to_channel(channel[0], torrent_def, extra_info, forward=True)
            return self.path

        def _on_added(added):
            request.write(json.dumps({"added": added}))
            request.finish()

        def _on_add_failed(failure):
            failure.trap(ValueError, DuplicateTorrentFileError)
            self._logger.exception(failure.value)
            request.write(BaseChannelsEndpoint.return_500(self, request, failure.value))
            request.finish()

        if self.path.startswith("http:") or self.path.startswith("https:"):
            self.deferred = http_get(self.path)
            self.deferred.addCallback(_on_url_fetched)

        if self.path.startswith("magnet:"):
            try:
                self.session.lm.ltmgr.get_metainfo(self.path, callback=self.deferred.callback,
                                                   timeout=30, timeout_callback=self.deferred.errback, notify=True)
            except Exception as ex:
                self.deferred.errback(ex)

            self.deferred.addCallback(_on_magnet_fetched)

        self.deferred.addCallback(_on_torrent_def_loaded)
        self.deferred.addCallback(_on_added)
        self.deferred.addErrback(_on_add_failed)
        return NOT_DONE_YET