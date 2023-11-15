    async def search(self, ctx: commands.Context, *, query: str):
        """Pick a track with a search.

        Use `[p]search list <search term>` to queue all tracks found on YouTube. `[p]search sc
        <search term>` will search SoundCloud instead of YouTube.
        """

        async def _search_menu(
            ctx: commands.Context,
            pages: list,
            controls: MutableMapping,
            message: discord.Message,
            page: int,
            timeout: float,
            emoji: str,
        ):
            if message:
                await self._search_button_action(ctx, tracks, emoji, page)
                with contextlib.suppress(discord.HTTPException):
                    await message.delete()
                return None

        search_controls = {
            "\N{DIGIT ONE}\N{COMBINING ENCLOSING KEYCAP}": _search_menu,
            "\N{DIGIT TWO}\N{COMBINING ENCLOSING KEYCAP}": _search_menu,
            "\N{DIGIT THREE}\N{COMBINING ENCLOSING KEYCAP}": _search_menu,
            "\N{DIGIT FOUR}\N{COMBINING ENCLOSING KEYCAP}": _search_menu,
            "\N{DIGIT FIVE}\N{COMBINING ENCLOSING KEYCAP}": _search_menu,
            "\N{LEFTWARDS BLACK ARROW}": prev_page,
            "\N{CROSS MARK}": close_menu,
            "\N{BLACK RIGHTWARDS ARROW}": next_page,
        }

        if not self._player_check(ctx):
            if self._connection_aborted:
                msg = _("Connection to Lavalink has failed")
                desc = EmptyEmbed
                if await ctx.bot.is_owner(ctx.author):
                    desc = _("Please check your console or logs for details.")
                return await self._embed_msg(ctx, title=msg, description=desc)
            try:
                if (
                    not ctx.author.voice.channel.permissions_for(ctx.me).connect
                    or not ctx.author.voice.channel.permissions_for(ctx.me).move_members
                    and userlimit(ctx.author.voice.channel)
                ):
                    return await self._embed_msg(
                        ctx,
                        title=_("Unable To Search For Tracks"),
                        description=_("I don't have permission to connect to your channel."),
                    )
                await lavalink.connect(ctx.author.voice.channel)
                player = lavalink.get_player(ctx.guild.id)
                player.store("connect", datetime.datetime.utcnow())
            except AttributeError:
                return await self._embed_msg(
                    ctx,
                    title=_("Unable To Search For Tracks"),
                    description=_("Connect to a voice channel first."),
                )
            except IndexError:
                return await self._embed_msg(
                    ctx,
                    title=_("Unable To Search For Tracks"),
                    description=_("Connection to Lavalink has not yet been established."),
                )
        player = lavalink.get_player(ctx.guild.id)
        guild_data = await self.config.guild(ctx.guild).all()
        player.store("channel", ctx.channel.id)
        player.store("guild", ctx.guild.id)
        if (
            not ctx.author.voice or ctx.author.voice.channel != player.channel
        ) and not await self._can_instaskip(ctx, ctx.author):
            return await self._embed_msg(
                ctx,
                title=_("Unable To Search For Tracks"),
                description=_("You must be in the voice channel to enqueue tracks."),
            )
        await self._eq_check(ctx, player)
        await self._data_check(ctx)

        before_queue_length = len(player.queue)

        if not isinstance(query, list):
            query = audio_dataclasses.Query.process_input(query)
            restrict = await self.config.restrict()
            if restrict and match_url(query):
                valid_url = url_check(query)
                if not valid_url:
                    return await self._embed_msg(
                        ctx,
                        title=_("Unable To Play Tracks"),
                        description=_("That URL is not allowed."),
                    )
            if not await is_allowed(ctx.guild, f"{query}", query_obj=query):
                return await self._embed_msg(
                    ctx,
                    title=_("Unable To Play Tracks"),
                    description=_("That track is not allowed."),
                )
            if query.invoked_from == "search list" or query.invoked_from == "local folder":
                if query.invoked_from == "search list" and not query.is_local:
                    try:
                        result, called_api = await self.music_cache.lavalink_query(
                            ctx, player, query
                        )
                    except TrackEnqueueError:
                        self._play_lock(ctx, False)
                        return await self._embed_msg(
                            ctx,
                            title=_("Unable to Get Track"),
                            description=_(
                                "I'm unable get a track from Lavalink at the moment, try again in a "
                                "few "
                                "minutes."
                            ),
                        )

                    tracks = result.tracks
                else:
                    try:
                        tracks = await self._folder_tracks(ctx, player, query)
                    except TrackEnqueueError:
                        self._play_lock(ctx, False)
                        return await self._embed_msg(
                            ctx,
                            title=_("Unable to Get Track"),
                            description=_(
                                "I'm unable get a track from Lavalink at the moment, try again in a "
                                "few "
                                "minutes."
                            ),
                        )
                if not tracks:
                    embed = discord.Embed(title=_("Nothing found."))
                    if await self.config.use_external_lavalink() and query.is_local:
                        embed.description = _(
                            "Local tracks will not work "
                            "if the `Lavalink.jar` cannot see the track.\n"
                            "This may be due to permissions or because Lavalink.jar is being run "
                            "in a different machine than the local tracks."
                        )
                    elif (
                        query.is_local
                        and query.suffix in audio_dataclasses._PARTIALLY_SUPPORTED_MUSIC_EXT
                    ):
                        embed = discord.Embed(title=_("Track is not playable."))
                        embed.description = _(
                            "**{suffix}** is not a fully supported format and some "
                            "tracks may not play."
                        ).format(suffix=query.suffix)
                    return await self._embed_msg(ctx, embed=embed)
                queue_dur = await queue_duration(ctx)
                queue_total_duration = lavalink.utils.format_time(queue_dur)
                if guild_data["dj_enabled"]:
                    if not await self._can_instaskip(ctx, ctx.author):
                        return await self._embed_msg(
                            ctx,
                            title=_("Unable To Play Tracks"),
                            description=_("You need the DJ role to queue tracks."),
                        )
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
                    if not player.current:
                        await player.play()
                player.maybe_shuffle(0 if empty_queue else 1)
                if len(tracks) > track_len:
                    maxlength_msg = " {bad_tracks} tracks cannot be queued.".format(
                        bad_tracks=(len(tracks) - track_len)
                    )
                else:
                    maxlength_msg = ""
                songembed = discord.Embed(
                    title=_("Queued {num} track(s).{maxlength_msg}").format(
                        num=track_len, maxlength_msg=maxlength_msg
                    )
                )
                if not guild_data["shuffle"] and queue_dur > 0:
                    songembed.set_footer(
                        text=_(
                            "{time} until start of search playback: starts at #{position} in queue"
                        ).format(time=queue_total_duration, position=before_queue_length + 1)
                    )
                return await self._embed_msg(ctx, embed=songembed)
            elif query.is_local and query.single_track:
                tracks = await self._folder_list(ctx, query)
            elif query.is_local and query.is_album:
                if ctx.invoked_with == "folder":
                    return await self._local_play_all(ctx, query, from_search=True)
                else:
                    tracks = await self._folder_list(ctx, query)
            else:
                try:
                    result, called_api = await self.music_cache.lavalink_query(ctx, player, query)
                except TrackEnqueueError:
                    self._play_lock(ctx, False)
                    return await self._embed_msg(
                        ctx,
                        title=_("Unable to Get Track"),
                        description=_(
                            "I'm unable get a track from Lavalink at the moment, try again in a few minutes."
                        ),
                    )
                tracks = result.tracks
            if not tracks:
                embed = discord.Embed(title=_("Nothing found."))
                if await self.config.use_external_lavalink() and query.is_local:
                    embed.description = _(
                        "Local tracks will not work "
                        "if the `Lavalink.jar` cannot see the track.\n"
                        "This may be due to permissions or because Lavalink.jar is being run "
                        "in a different machine than the local tracks."
                    )
                elif (
                    query.is_local
                    and query.suffix in audio_dataclasses._PARTIALLY_SUPPORTED_MUSIC_EXT
                ):
                    embed = discord.Embed(title=_("Track is not playable."))
                    embed.description = _(
                        "**{suffix}** is not a fully supported format and some "
                        "tracks may not play."
                    ).format(suffix=query.suffix)
                return await self._embed_msg(ctx, embed=embed)
        else:
            tracks = query

        dj_enabled = self._dj_status_cache.setdefault(
            ctx.guild.id, await self.config.guild(ctx.guild).dj_enabled()
        )

        len_search_pages = math.ceil(len(tracks) / 5)
        search_page_list = []
        for page_num in range(1, len_search_pages + 1):
            embed = await self._build_search_page(ctx, tracks, page_num)
            search_page_list.append(embed)

        if dj_enabled and not await self._can_instaskip(ctx, ctx.author):
            return await menu(ctx, search_page_list, DEFAULT_CONTROLS)

        await menu(ctx, search_page_list, search_controls)