    async def play_query(
        self,
        query: str,
        guild: discord.Guild,
        channel: discord.VoiceChannel,
        is_autoplay: bool = True,
    ):
        if not self._player_check(guild.me):
            try:
                if (
                    not channel.permissions_for(guild.me).connect
                    or not channel.permissions_for(guild.me).move_members
                    and userlimit(channel)
                ):
                    log.error(f"I don't have permission to connect to {channel} in {guild}.")

                await lavalink.connect(channel)
                player = lavalink.get_player(guild.id)
                player.store("connect", datetime.datetime.utcnow())
            except IndexError:
                log.debug(
                    f"Connection to Lavalink has not yet been established"
                    f" while trying to connect to to {channel} in {guild}."
                )
                return

        player = lavalink.get_player(guild.id)

        player.store("channel", channel.id)
        player.store("guild", guild.id)
        await self._data_check(guild.me)
        query = audio_dataclasses.Query.process_input(query)
        ctx = namedtuple("Context", "message")
        results, called_api = await self.music_cache.lavalink_query(ctx(guild), player, query)

        if not results.tracks:
            log.debug(f"Query returned no tracks.")
            return
        track = results.tracks[0]

        if not await is_allowed(
            guild, f"{track.title} {track.author} {track.uri} {str(query._raw)}"
        ):
            log.debug(f"Query is not allowed in {guild} ({guild.id})")
            return
        track.extras = {"autoplay": is_autoplay}
        player.add(player.channel.guild.me, track)
        self.bot.dispatch(
            "red_audio_track_auto_play", player.channel.guild, track, player.channel.guild.me
        )
        if not player.current:
            await player.play()