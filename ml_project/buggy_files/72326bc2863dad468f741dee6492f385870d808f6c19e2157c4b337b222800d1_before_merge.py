    def _get_streams(self):
        match = _url_re.match(self.url)
        if not match:
            return

        channel, media_id = match.group("channel", "media_id")
        self.logger.debug("Matched URL: channel={0}, media_id={1}".format(channel, media_id))
        if not media_id:
            res = http.get(LIVE_API.format(channel))
            livestream = http.json(res, schema=_live_schema)
            if livestream["media_hosted_media"]:
                hosted = _live_schema.validate(livestream["media_hosted_media"])
                self.logger.info("{0} is hosting {1}", livestream["media_user_name"], hosted["media_user_name"])
                livestream = hosted

            if not livestream["media_is_live"]:
                return

            media_id = livestream["media_id"]
            media_type = "live"
        else:
            media_type = "video"

        res = http.get(PLAYER_API.format(media_type, media_id))
        player = http.json(res, schema=_player_schema)

        if media_type == "live":
            return self._get_live_streams(player)
        else:
            return self._get_video_streams(player)