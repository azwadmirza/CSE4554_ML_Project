    async def event_handler(
        self, player: lavalink.Player, event_type: lavalink.LavalinkEvents, extra
    ):
        disconnect = await self.config.guild(player.channel.guild).disconnect()
        autoplay = await self.config.guild(player.channel.guild).auto_play() or self.owns_autoplay
        notify = await self.config.guild(player.channel.guild).notify()
        status = await self.config.status()
        repeat = await self.config.guild(player.channel.guild).repeat()

        async def _players_check():
            try:
                get_single_title = lavalink.active_players()[0].current.title
                query = audio_dataclasses.Query.process_input(
                    lavalink.active_players()[0].current.uri
                )
                if get_single_title == "Unknown title":
                    get_single_title = lavalink.active_players()[0].current.uri
                    if not get_single_title.startswith("http"):
                        get_single_title = get_single_title.rsplit("/", 1)[-1]
                elif query.is_local:
                    get_single_title = "{} - {}".format(
                        lavalink.active_players()[0].current.author,
                        lavalink.active_players()[0].current.title,
                    )
                else:
                    get_single_title = lavalink.active_players()[0].current.title
                playing_servers = len(lavalink.active_players())
            except IndexError:
                get_single_title = None
                playing_servers = 0
            return get_single_title, playing_servers

        async def _status_check(playing_servers):
            if playing_servers == 0:
                await self.bot.change_presence(activity=None)
            if playing_servers == 1:
                single_title = await _players_check()
                await self.bot.change_presence(
                    activity=discord.Activity(
                        name=single_title[0], type=discord.ActivityType.listening
                    )
                )
            if playing_servers > 1:
                await self.bot.change_presence(
                    activity=discord.Activity(
                        name=_("music in {} servers").format(playing_servers),
                        type=discord.ActivityType.playing,
                    )
                )

        if event_type == lavalink.LavalinkEvents.TRACK_START:
            self.skip_votes[player.channel.guild] = []
            playing_song = player.fetch("playing_song")
            requester = player.fetch("requester")
            player.store("prev_song", playing_song)
            player.store("prev_requester", requester)
            player.store("playing_song", player.current)
            player.store(
                "requester", player.current.requester if player.current else player.current
            )
            self.bot.dispatch(
                "red_audio_track_start",
                player.channel.guild,
                player.current,
                player.current.requester,
            )
        if event_type == lavalink.LavalinkEvents.TRACK_END:
            prev_song = player.fetch("prev_song")
            prev_requester = player.fetch("prev_requester")
            self.bot.dispatch(
                "red_audio_track_end", player.channel.guild, prev_song, prev_requester
            )

        if event_type == lavalink.LavalinkEvents.QUEUE_END:
            prev_song = player.fetch("prev_song")
            prev_requester = player.fetch("prev_requester")
            self.bot.dispatch(
                "red_audio_queue_end", player.channel.guild, prev_song, prev_requester
            )
            if autoplay and not player.queue and player.fetch("playing_song") is not None:
                if self.owns_autoplay is None:
                    try:
                        await self.music_cache.autoplay(player)
                    except DatabaseError:
                        notify_channel = player.fetch("channel")
                        if notify_channel:
                            notify_channel = self.bot.get_channel(notify_channel)
                            await self._embed_msg(
                                notify_channel, _("Autoplay: Couldn't get a valid track.")
                            )
                        return
                else:
                    self.bot.dispatch(
                        "red_audio_should_auto_play",
                        player,
                        player.channel.guild,
                        player.channel,
                        self.play_query,
                    )

        if event_type == lavalink.LavalinkEvents.TRACK_START and notify:
            notify_channel = player.fetch("channel")
            prev_song = player.fetch("prev_song")
            if notify_channel:
                notify_channel = self.bot.get_channel(notify_channel)
                if player.fetch("notify_message") is not None:
                    with contextlib.suppress(discord.HTTPException):
                        await player.fetch("notify_message").delete()

                if (
                    autoplay
                    and player.current.extras.get("autoplay")
                    and (prev_song is None or not prev_song.extras.get("autoplay"))
                ):
                    embed = discord.Embed(
                        colour=(await self.bot.get_embed_colour(notify_channel)),
                        title=_("Auto play started."),
                    )
                    await notify_channel.send(embed=embed)

                query = audio_dataclasses.Query.process_input(player.current.uri)

                if query.is_local if player.current else False:
                    if player.current.title != "Unknown title":
                        description = "**{} - {}**\n{}".format(
                            player.current.author,
                            player.current.title,
                            audio_dataclasses.LocalPath(player.current.uri).to_string_hidden(),
                        )
                    else:
                        description = "{}".format(
                            audio_dataclasses.LocalPath(player.current.uri).to_string_hidden()
                        )
                else:
                    description = "**[{}]({})**".format(player.current.title, player.current.uri)
                if player.current.is_stream:
                    dur = "LIVE"
                else:
                    dur = lavalink.utils.format_time(player.current.length)
                embed = discord.Embed(
                    colour=(await self.bot.get_embed_color(notify_channel)),
                    title=_("Now Playing"),
                    description=description,
                )
                embed.set_footer(
                    text=_("Track length: {length} | Requested by: {user}").format(
                        length=dur, user=player.current.requester
                    )
                )
                if (
                    await self.config.guild(player.channel.guild).thumbnail()
                    and player.current.thumbnail
                ):
                    embed.set_thumbnail(url=player.current.thumbnail)
                notify_message = await notify_channel.send(embed=embed)
                player.store("notify_message", notify_message)

        if event_type == lavalink.LavalinkEvents.TRACK_START and status:
            player_check = await _players_check()
            await _status_check(player_check[1])

        if event_type == lavalink.LavalinkEvents.TRACK_END and status:
            await asyncio.sleep(1)
            if not player.is_playing:
                player_check = await _players_check()
                await _status_check(player_check[1])

        if event_type == lavalink.LavalinkEvents.QUEUE_END and notify and not autoplay:
            notify_channel = player.fetch("channel")
            if notify_channel:
                notify_channel = self.bot.get_channel(notify_channel)
                embed = discord.Embed(
                    colour=(await self.bot.get_embed_colour(notify_channel)),
                    title=_("Queue ended."),
                )
                await notify_channel.send(embed=embed)

        elif event_type == lavalink.LavalinkEvents.QUEUE_END and disconnect and not autoplay:
            self.bot.dispatch("red_audio_audio_disconnect", player.channel.guild)
            await player.disconnect()

        if event_type == lavalink.LavalinkEvents.QUEUE_END and status:
            player_check = await _players_check()
            await _status_check(player_check[1])

        if event_type == lavalink.LavalinkEvents.TRACK_EXCEPTION:
            message_channel = player.fetch("channel")
            if message_channel:
                message_channel = self.bot.get_channel(message_channel)
                query = audio_dataclasses.Query.process_input(player.current.uri)
                if player.current and query.is_local:
                    query = audio_dataclasses.Query.process_input(player.current.uri)
                    if player.current.title == "Unknown title":
                        description = "{}".format(query.track.to_string_hidden())
                    else:
                        song = bold("{} - {}").format(player.current.author, player.current.title)
                        description = "{}\n{}".format(song, query.track.to_string_hidden())
                else:
                    description = bold("[{}]({})").format(player.current.title, player.current.uri)

                embed = discord.Embed(
                    colour=(await self.bot.get_embed_color(message_channel)),
                    title=_("Track Error"),
                    description="{}\n{}".format(extra, description),
                )
                embed.set_footer(text=_("Skipping..."))
                await message_channel.send(embed=embed)
            while True:
                if player.current in player.queue:
                    player.queue.remove(player.current)
                else:
                    break
            if repeat:
                player.current = None
            await player.skip()