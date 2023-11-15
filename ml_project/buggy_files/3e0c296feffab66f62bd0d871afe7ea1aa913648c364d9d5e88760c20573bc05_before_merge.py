    async def _search_button_action(self, ctx: commands.Context, tracks, emoji, page):
        if not self._player_check(ctx):
            if self._connection_aborted:
                msg = _("Connection to Lavalink has failed.")
                if await ctx.bot.is_owner(ctx.author):
                    msg += " " + _("Please check your console or logs for details.")
                return await self._embed_msg(ctx, msg)
            try:
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
        if not await self._currency_check(ctx, guild_data["jukebox_price"]):
            return
        try:
            if emoji == "1⃣":
                search_choice = tracks[0 + (page * 5)]
            elif emoji == "2⃣":
                search_choice = tracks[1 + (page * 5)]
            elif emoji == "3⃣":
                search_choice = tracks[2 + (page * 5)]
            elif emoji == "4⃣":
                search_choice = tracks[3 + (page * 5)]
            elif emoji == "5⃣":
                search_choice = tracks[4 + (page * 5)]
            else:
                search_choice = tracks[0 + (page * 5)]
                # TODO: verify this does not break exit and arrows
        except IndexError:
            search_choice = tracks[-1]
        try:
            query = audio_dataclasses.Query.process_input(search_choice.uri)
            if query.is_local:

                localtrack = audio_dataclasses.LocalPath(search_choice.uri)
                if search_choice.title != "Unknown title":
                    description = "**{} - {}**\n{}".format(
                        search_choice.author, search_choice.title, localtrack.to_string_hidden()
                    )
                else:
                    description = localtrack.to_string_hidden()
            else:
                description = "**[{}]({})**".format(search_choice.title, search_choice.uri)

        except AttributeError:
            search_choice = audio_dataclasses.Query.process_input(search_choice)
            if search_choice.track.exists() and search_choice.track.is_dir():
                return await ctx.invoke(self.search, query=search_choice)
            elif search_choice.track.exists() and search_choice.track.is_file():
                search_choice.invoked_from = "localtrack"
            return await ctx.invoke(self.play, query=search_choice)

        embed = discord.Embed(
            colour=await ctx.embed_colour(), title=_("Track Enqueued"), description=description
        )
        queue_dur = await queue_duration(ctx)
        queue_total_duration = lavalink.utils.format_time(queue_dur)
        if not await is_allowed(
            ctx.guild,
            (
                f"{search_choice.title} {search_choice.author} {search_choice.uri} "
                f"{str(audio_dataclasses.Query.process_input(search_choice))}"
            ),
        ):
            log.debug(f"Query is not allowed in {ctx.guild} ({ctx.guild.id})")
            self._play_lock(ctx, False)
            return await self._embed_msg(ctx, _("This track is not allowed in this server."))
        elif guild_data["maxlength"] > 0:

            if track_limit(search_choice.length, guild_data["maxlength"]):
                player.add(ctx.author, search_choice)
                player.maybe_shuffle()
                self.bot.dispatch(
                    "red_audio_track_enqueue", player.channel.guild, search_choice, ctx.author
                )
            else:
                return await self._embed_msg(ctx, _("Track exceeds maximum length."))
        else:
            player.add(ctx.author, search_choice)
            player.maybe_shuffle()
            self.bot.dispatch(
                "red_audio_track_enqueue", player.channel.guild, search_choice, ctx.author
            )

        if not guild_data["shuffle"] and queue_dur > 0:
            embed.set_footer(
                text=_("{time} until track playback: #{position} in queue").format(
                    time=queue_total_duration, position=len(player.queue) + 1
                )
            )

        if not player.current:
            await player.play()
        await ctx.send(embed=embed)