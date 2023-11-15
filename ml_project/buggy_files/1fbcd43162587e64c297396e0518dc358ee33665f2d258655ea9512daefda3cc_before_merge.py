    async def load_streams(self):
        streams = []

        for raw_stream in await self.db.streams():
            _class = getattr(_streamtypes, raw_stream["type"], None)
            if not _class:
                continue
            raw_msg_cache = raw_stream["messages"]
            raw_stream["_messages_cache"] = []
            for raw_msg in raw_msg_cache:
                chn = self.bot.get_channel(raw_msg["channel"])
                msg = await chn.get_message(raw_msg["message"])
                raw_stream["_messages_cache"].append(msg)
            token = await self.db.tokens.get_raw(_class.__name__, default=None)
            if token is not None:
                raw_stream["token"] = token
            streams.append(_class(**raw_stream))

        return streams