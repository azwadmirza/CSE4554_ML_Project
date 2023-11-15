    async def _migrate_config(self, from_version: int, to_version: int):
        database_entries = []
        time_now = str(datetime.datetime.now(datetime.timezone.utc))
        if from_version == to_version:
            return
        elif from_version < to_version:
            all_guild_data = await self.config.all_guilds()
            all_playlist = {}
            for guild_id, guild_data in all_guild_data.items():
                temp_guild_playlist = guild_data.pop("playlists", None)
                if temp_guild_playlist:
                    guild_playlist = {}
                    for count, (name, data) in enumerate(temp_guild_playlist.items(), 1):
                        if not data or not name:
                            continue
                        playlist = {"id": count, "name": name, "guild": int(guild_id)}
                        playlist.update(data)
                        guild_playlist[str(count)] = playlist

                        tracks_in_playlist = data.get("tracks", []) or []
                        for t in tracks_in_playlist:
                            uri = t.get("info", {}).get("uri")
                            if uri:
                                t = {"loadType": "V2_COMPAT", "tracks": [t], "query": uri}
                                database_entries.append(
                                    {
                                        "query": uri,
                                        "data": json.dumps(t),
                                        "last_updated": time_now,
                                        "last_fetched": time_now,
                                    }
                                )
                    if guild_playlist:
                        all_playlist[str(guild_id)] = guild_playlist
            await self.config.custom(PlaylistScope.GUILD.value).set(all_playlist)
            # new schema is now in place
            await self.config.schema_version.set(_SCHEMA_VERSION)

            # migration done, now let's delete all the old stuff
            for guild_id in all_guild_data:
                await self.config.guild(
                    cast(discord.Guild, discord.Object(id=guild_id))
                ).clear_raw("playlists")
        if database_entries and HAS_SQL:
            await self.music_cache.insert("lavalink", database_entries)