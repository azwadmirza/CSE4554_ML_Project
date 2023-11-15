    async def _enqueue_tracks(
        self, ctx: commands.Context, query: Union[audio_dataclasses.Query, list]
    ):
        player = lavalink.get_player(ctx.guild.id)
        try:
            if self.play_lock[ctx.message.guild.id]:
                return await self._embed_msg(
                    ctx, _("Wait until the playlist has finished loading.")
                )
        except KeyError:
            self._play_lock(ctx, True)
        guild_data = await self.config.guild(ctx.guild).all()
        first_track_only = False
        index = None
        playlist_data = None
        seek = 0
        if type(query) is not list:

            if query.single_track:
                first_track_only = True
                index = query.track_index
                if query.start_time:
                    seek = query.start_time
            result, called_api = await self.music_cache.lavalink_query(ctx, player, query)
            tracks = result.tracks
            playlist_data = result.playlist_info
            if not tracks:
                self._play_lock(ctx, False)
                embed = discord.Embed(title=_("Nothing found."), colour=await ctx.embed_colour())
                if result.exception_message:
                    embed.set_footer(text=result.exception_message)
                if await self.config.use_external_lavalink() and query.is_local:
                    embed.description = _(
                        "Local tracks will not work "
                        "if the `Lavalink.jar` cannot see the track.\n"
                        "This may be due to permissions or because Lavalink.jar is being run "
                        "in a different machine than the local tracks."
                    )
                return await ctx.send(embed=embed)
        else:
            tracks = query
        queue_dur = await queue_duration(ctx)
        queue_total_duration = lavalink.utils.format_time(queue_dur)
        before_queue_length = len(player.queue)

        if not first_track_only and len(tracks) > 1:
            # a list of Tracks where all should be enqueued
            # this is a Spotify playlist aleady made into a list of Tracks or a
            # url where Lavalink handles providing all Track objects to use, like a
            # YouTube or Soundcloud playlist
            track_len = 0
            empty_queue = not player.queue
            for track in tracks:
                if not await is_allowed(
                    ctx.guild,
                    (
                        f"{track.title} {track.author} {track.uri} "
                        f"{str(audio_dataclasses.Query.process_input(track))}"
                    ),
                ):
                    log.debug(f"Query is not allowed in {ctx.guild} ({ctx.guild.id})")
                    continue
                elif guild_data["maxlength"] > 0:
                    if track_limit(track, guild_data["maxlength"]):
                        track_len += 1
                        player.add(ctx.author, track)
                        self.bot.dispatch(
                            "red_audio_track_enqueue", player.channel.guild, track, ctx.author
                        )

                else:
                    track_len += 1
                    player.add(ctx.author, track)
                    self.bot.dispatch(
                        "red_audio_track_enqueue", player.channel.guild, track, ctx.author
                    )
            player.maybe_shuffle(0 if empty_queue else 1)

            if len(tracks) > track_len:
                maxlength_msg = " {bad_tracks} tracks cannot be queued.".format(
                    bad_tracks=(len(tracks) - track_len)
                )
            else:
                maxlength_msg = ""
            embed = discord.Embed(
                colour=await ctx.embed_colour(),
                description="{name}".format(
                    name=playlist_data.name if playlist_data else _("No Title")
                ),
                title=_("Playlist Enqueued"),
            )
            embed.set_footer(
                text=_("Added {num} tracks to the queue.{maxlength_msg}").format(
                    num=track_len, maxlength_msg=maxlength_msg
                )
            )
            if not guild_data["shuffle"] and queue_dur > 0:
                embed.set_footer(
                    text=_(
                        "{time} until start of playlist playback: starts at #{position} in queue"
                    ).format(time=queue_total_duration, position=before_queue_length + 1)
                )
            if not player.current:
                await player.play()
        else:
            # a ytsearch: prefixed item where we only need the first Track returned
            # this is in the case of [p]play <query>, a single Spotify url/code
            # or this is a localtrack item
            try:

                single_track = tracks[index] if index else tracks[0]
                if seek and seek > 0:
                    single_track.start_timestamp = seek * 1000
                if not await is_allowed(
                    ctx.guild,
                    (
                        f"{single_track.title} {single_track.author} {single_track.uri} "
                        f"{str(audio_dataclasses.Query.process_input(single_track))}"
                    ),
                ):
                    log.debug(f"Query is not allowed in {ctx.guild} ({ctx.guild.id})")
                    self._play_lock(ctx, False)
                    return await self._embed_msg(
                        ctx, _("This track is not allowed in this server.")
                    )
                elif guild_data["maxlength"] > 0:
                    if track_limit(single_track, guild_data["maxlength"]):
                        player.add(ctx.author, single_track)
                        player.maybe_shuffle()
                        self.bot.dispatch(
                            "red_audio_track_enqueue",
                            player.channel.guild,
                            single_track,
                            ctx.author,
                        )
                    else:
                        self._play_lock(ctx, False)
                        return await self._embed_msg(ctx, _("Track exceeds maximum length."))

                else:
                    player.add(ctx.author, single_track)
                    player.maybe_shuffle()
                    self.bot.dispatch(
                        "red_audio_track_enqueue", player.channel.guild, single_track, ctx.author
                    )
            except IndexError:
                self._play_lock(ctx, False)
                return await self._embed_msg(
                    ctx, _("Nothing found. Check your Lavalink logs for details.")
                )
            query = audio_dataclasses.Query.process_input(single_track.uri)
            if query.is_local:
                if single_track.title != "Unknown title":
                    description = "**{} - {}**\n{}".format(
                        single_track.author,
                        single_track.title,
                        audio_dataclasses.LocalPath(single_track.uri).to_string_hidden(),
                    )
                else:
                    description = "{}".format(
                        audio_dataclasses.LocalPath(single_track.uri).to_string_hidden()
                    )
            else:
                description = "**[{}]({})**".format(single_track.title, single_track.uri)
            embed = discord.Embed(
                colour=await ctx.embed_colour(), title=_("Track Enqueued"), description=description
            )
            if not guild_data["shuffle"] and queue_dur > 0:
                embed.set_footer(
                    text=_("{time} until track playback: #{position} in queue").format(
                        time=queue_total_duration, position=before_queue_length + 1
                    )
                )

        await ctx.send(embed=embed)
        if not player.current:
            await player.play()

        self._play_lock(ctx, False)