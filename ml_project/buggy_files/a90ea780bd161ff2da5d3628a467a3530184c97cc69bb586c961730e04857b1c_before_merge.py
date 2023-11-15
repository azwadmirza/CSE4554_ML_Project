    async def now(self, ctx: commands.Context):
        """Now playing."""
        if not self._player_check(ctx):
            return await self._embed_msg(ctx, _("Nothing playing."))
        expected = ("⏮", "⏹", "⏯", "⏭")
        emoji = {"prev": "⏮", "stop": "⏹", "pause": "⏯", "next": "⏭"}
        player = lavalink.get_player(ctx.guild.id)
        if player.current:
            arrow = await draw_time(ctx)
            pos = lavalink.utils.format_time(player.position)
            if player.current.is_stream:
                dur = "LIVE"
            else:
                dur = lavalink.utils.format_time(player.current.length)
            query = audio_dataclasses.Query.process_input(player.current.uri)
            if query.is_local:
                if not player.current.title == "Unknown title":
                    song = "**{track.author} - {track.title}**\n{uri}\n"
                else:
                    song = "{uri}\n"
            else:
                song = "**[{track.title}]({track.uri})**\n"
            song += _("Requested by: **{track.requester}**")
            song += "\n\n{arrow}`{pos}`/`{dur}`"
            song = song.format(
                track=player.current,
                uri=audio_dataclasses.LocalPath(player.current.uri).to_string_hidden()
                if audio_dataclasses.Query.process_input(player.current.uri).is_local
                else player.current.uri,
                arrow=arrow,
                pos=pos,
                dur=dur,
            )
        else:
            song = _("Nothing.")

        if player.fetch("np_message") is not None:
            with contextlib.suppress(discord.HTTPException):
                await player.fetch("np_message").delete()

        embed = discord.Embed(
            colour=await ctx.embed_colour(), title=_("Now Playing"), description=song
        )
        if await self.config.guild(ctx.guild).thumbnail() and player.current:
            if player.current.thumbnail:
                embed.set_thumbnail(url=player.current.thumbnail)

        shuffle = await self.config.guild(ctx.guild).shuffle()
        repeat = await self.config.guild(ctx.guild).repeat()
        autoplay = await self.config.guild(ctx.guild).auto_play() or self.owns_autoplay
        text = ""
        text += (
            _("Auto-Play")
            + ": "
            + ("\N{WHITE HEAVY CHECK MARK}" if autoplay else "\N{CROSS MARK}")
        )
        text += (
            (" | " if text else "")
            + _("Shuffle")
            + ": "
            + ("\N{WHITE HEAVY CHECK MARK}" if shuffle else "\N{CROSS MARK}")
        )
        text += (
            (" | " if text else "")
            + _("Repeat")
            + ": "
            + ("\N{WHITE HEAVY CHECK MARK}" if repeat else "\N{CROSS MARK}")
        )
        embed.set_footer(text=text)

        message = await ctx.send(embed=embed)

        player.store("np_message", message)

        dj_enabled = await self.config.guild(ctx.guild).dj_enabled()
        vote_enabled = await self.config.guild(ctx.guild).vote_enabled()
        if dj_enabled or vote_enabled:
            if not await self._can_instaskip(ctx, ctx.author) and not await self._is_alone(ctx):
                return

        if player.current:
            task = start_adding_reactions(message, expected[:4], ctx.bot.loop)
        else:
            task = None

        try:
            (r, u) = await self.bot.wait_for(
                "reaction_add",
                check=ReactionPredicate.with_emojis(expected, message, ctx.author),
                timeout=30.0,
            )
        except asyncio.TimeoutError:
            return await self._clear_react(message, emoji)
        else:
            if task is not None:
                task.cancel()
        reacts = {v: k for k, v in emoji.items()}
        react = reacts[r.emoji]
        if react == "prev":
            await self._clear_react(message, emoji)
            await ctx.invoke(self.prev)
        elif react == "stop":
            await self._clear_react(message, emoji)
            await ctx.invoke(self.stop)
        elif react == "pause":
            await self._clear_react(message, emoji)
            await ctx.invoke(self.pause)
        elif react == "next":
            await self._clear_react(message, emoji)
            await ctx.invoke(self.skip)