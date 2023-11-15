    async def search(self, ctx: commands.Context, *, query: str):
        """Pick a track with a search.

        Use `[p]search list <search term>` to queue all tracks found
        on YouTube. `[p]search sc <search term>` will search SoundCloud
        instead of YouTube.
        """

        async def _search_menu(
            ctx: commands.Context,
            pages: list,
            controls: dict,
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
            "1⃣": _search_menu,
            "2⃣": _search_menu,
            "3⃣": _search_menu,
            "4⃣": _search_menu,
            "5⃣": _search_menu,
            "⬅": prev_page,
            "❌": close_menu,
            "➡": next_page,
        }

        if not self._player_check(ctx):
            if self._connection_aborted:
                msg = _("Connection to Lavalink has failed.")
                if await ctx.bot.is_owner(ctx.author):
                    msg += " " + _("Please check your console or logs for details.")
                return await self._embed_msg(ctx, msg)
            try:
                if (
                    not ctx.author.voice.channel.permissions_for(ctx.me).connect
                    or not ctx.author.voice.channel.permissions_for(ctx.me).move_members
                    and userlimit(ctx.author.voice.channel)
                ):
                    return await self._embed_msg(
                        ctx, _("I don't have permission to connect to your channel.")
                    )
                await lavalink.connect(ctx.author.voice.channel)
                player = lavalink.get_player(ctx.guild.id)
                player.store("connect", datetime.datetime.utcnow())
            except AttributeError:
                return await self._embed_msg(ctx, _("Connect to a voice channel first."))
            except IndexError:
                return await self._embed_msg(
                    ctx, _("Connection to Lavalink has not yet been established.")
                )
        player = lavalink.get_player(ctx.guild.id)
        guild_data = await self.config.guild(ctx.guild).all()
        player.store("channel", ctx.channel.id)
        player.store("guild", ctx.guild.id)
        if (
            not ctx.author.voice or ctx.author.voice.channel != player.channel
        ) and not await self._can_instaskip(ctx, ctx.author):
            return await self._embed_msg(
                ctx, _("You must be in the voice channel to enqueue tracks.")
            )
        await self._eq_check(ctx, player)
        await self._data_check(ctx)

        if not isinstance(query, list):
            query = audio_dataclasses.Query.process_input(query)
            if query.invoked_from == "search list" or query.invoked_from == "local folder":
                if query.invoked_from == "search list":
                    result, called_api = await self.music_cache.lavalink_query(ctx, player, query)
                    tracks = result.tracks
                else:
                    tracks = await self._folder_tracks(ctx, player, query)
                if not tracks:
                    embed = discord.Embed(
                        title=_("Nothing found."), colour=await ctx.embed_colour()
                    )
                    if await self.config.use_external_lavalink() and query.is_local:
                        embed.description = _(
                            "Local tracks will not work "
                            "if the `Lavalink.jar` cannot see the track.\n"
                            "This may be due to permissions or because Lavalink.jar is being run "
                            "in a different machine than the local tracks."
                        )
                    return await ctx.send(embed=embed)
                queue_dur = await queue_duration(ctx)
                queue_total_duration = lavalink.utils.format_time(queue_dur)

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
                    colour=await ctx.embed_colour(),
                    title=_("Queued {num} track(s).{maxlength_msg}").format(
                        num=track_len, maxlength_msg=maxlength_msg
                    ),
                )
                if not guild_data["shuffle"] and queue_dur > 0:
                    songembed.set_footer(
                        text=_(
                            "{time} until start of search playback: starts at #{position} in queue"
                        ).format(time=queue_total_duration, position=len(player.queue) + 1)
                    )
                return await ctx.send(embed=songembed)
            elif query.is_local and query.single_track:
                tracks = await self._folder_list(ctx, query)
            elif query.is_local and query.is_album:
                if ctx.invoked_with == "folder":
                    return await self._local_play_all(ctx, query, from_search=True)
                else:
                    tracks = await self._folder_list(ctx, query)
            else:
                result, called_api = await self.music_cache.lavalink_query(ctx, player, query)
                tracks = result.tracks
            if not tracks:
                embed = discord.Embed(title=_("Nothing found."), colour=await ctx.embed_colour())
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

        len_search_pages = math.ceil(len(tracks) / 5)
        search_page_list = []
        for page_num in range(1, len_search_pages + 1):
            embed = await self._build_search_page(ctx, tracks, page_num)
            search_page_list.append(embed)

        dj_enabled = await self.config.guild(ctx.guild).dj_enabled()
        if dj_enabled:
            if not await self._can_instaskip(ctx, ctx.author):
                return await menu(ctx, search_page_list, DEFAULT_CONTROLS)

        await menu(ctx, search_page_list, search_controls)