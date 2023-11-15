    def _get_streams(self):
        api = self._create_api()
        match = _url_re.match(self.url)
        media_id = int(match.group("media_id"))

        try:
            # the media.stream_data field is required, no stream data is returned otherwise
            info = api.get_info(media_id, fields=["media.stream_data"], schema=_media_schema)
        except CrunchyrollAPIError as err:
            raise PluginError(u"Media lookup error: {0}".format(err.msg))

        if not info:
            return

        streams = {}

        # The adaptive quality stream sometimes a subset of all the other streams listed, ultra is no included
        has_adaptive = any([s[u"quality"] == u"adaptive" for s in info[u"streams"]])
        if has_adaptive:
            self.logger.debug(u"Loading streams from adaptive playlist")
            for stream in filter(lambda x: x[u"quality"] == u"adaptive", info[u"streams"]):
                for q, s in HLSStream.parse_variant_playlist(self.session, stream[u"url"]).items():
                    # rename the bitrates to low, mid, or high. ultra doesn't seem to appear in the adaptive streams
                    name = STREAM_NAMES.get(q, q)
                    streams[name] = s

        # If there is no adaptive quality stream then parse each individual result
        for stream in info[u"streams"]:
            if stream[u"quality"] != u"adaptive":
                # the video_encode_id indicates that the stream is not a variant playlist
                if u"video_encode_id" in stream:
                    streams[stream[u"quality"]] = HLSStream(self.session, stream[u"url"])
                else:
                    # otherwise the stream url is actually a list of stream qualities
                    for q, s in HLSStream.parse_variant_playlist(self.session, stream[u"url"]).items():
                        # rename the bitrates to low, mid, or high. ultra doesn't seem to appear in the adaptive streams
                        name = STREAM_NAMES.get(q, q)
                        streams[name] = s

        return streams