    async def load_communities(self):
        communities = []

        for raw_community in await self.db.communities():
            _class = getattr(_streamtypes, raw_community["type"], None)
            if not _class:
                continue
            raw_msg_cache = raw_community["messages"]
            raw_community["_messages_cache"] = []
            for raw_msg in raw_msg_cache:
                chn = self.bot.get_channel(raw_msg["channel"])
                msg = await chn.get_message(raw_msg["message"])
                raw_community["_messages_cache"].append(msg)
            token = await self.db.tokens.get_raw(_class.__name__, default=None)
            communities.append(_class(token=token, **raw_community))

        # issue 1191 extended resolution: Remove this after suitable period
        # Fast dedupe below
        seen = set()
        seen_add = seen.add
        return [x for x in communities if not (x.name.lower() in seen or seen_add(x.name.lower()))]