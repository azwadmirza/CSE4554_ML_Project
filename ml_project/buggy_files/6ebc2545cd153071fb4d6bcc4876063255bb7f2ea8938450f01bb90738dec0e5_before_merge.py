    async def load_streams(self):
        streams = []

        for raw_stream in await self.db.streams():
            _class = getattr(StreamClasses, raw_stream["type"], None)
            if not _class:
                continue
            raw_msg_cache = raw_stream["messages"]
            raw_stream["_messages_cache"] = []
            for raw_msg in raw_msg_cache:
                chn = self.bot.get_channel(raw_msg["channel"])
                msg = await chn.get_message(raw_msg["message"])
                raw_stream["_messages_cache"].append(msg)
            token = await self.db.tokens.get_raw(_class.__name__)
            streams.append(_class(token=token, **raw_stream))

        # issue 1191 extended resolution: Remove this after suitable period
        # Fast dedupe below
        seen = set()
        seen_add = seen.add
        return [x for x in streams if not (x.name.lower() in seen or seen_add(x.name.lower()))]