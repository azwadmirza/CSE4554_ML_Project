    async def pause(self, ctx: commands.Context):
        """Pause or resume a playing track."""
        dj_enabled = await self.config.guild(ctx.guild).dj_enabled()
        if not self._player_check(ctx):
            return await self._embed_msg(ctx, _("Nothing playing."))
        player = lavalink.get_player(ctx.guild.id)
        if (
            not ctx.author.voice or ctx.author.voice.channel != player.channel
        ) and not await self._can_instaskip(ctx, ctx.author):
            return await self._embed_msg(
                ctx, _("You must be in the voice channel pause or resume.")
            )
        if dj_enabled:
            if not await self._can_instaskip(ctx, ctx.author) and not await self._is_alone(ctx):
                return await self._embed_msg(
                    ctx, _("You need the DJ role to pause or resume tracks.")
                )

        if not player.current:
            return await self._embed_msg(ctx, _("Nothing playing."))
        query = audio_dataclasses.Query.process_input(player.current.uri)
        if query.is_local:
            query = audio_dataclasses.Query.process_input(player.current.uri)
            if player.current.title == "Unknown title":
                description = "{}".format(query.track.to_string_hidden())
            else:
                song = bold("{} - {}").format(player.current.author, player.current.title)
                description = "{}\n{}".format(song, query.track.to_string_hidden())
        else:
            description = bold("[{}]({})").format(player.current.title, player.current.uri)

        if player.current and not player.paused:
            await player.pause()
            embed = discord.Embed(
                colour=await ctx.embed_colour(), title=_("Track Paused"), description=description
            )
            return await ctx.send(embed=embed)
        if player.current and player.paused:
            await player.pause(False)
            embed = discord.Embed(
                colour=await ctx.embed_colour(), title=_("Track Resumed"), description=description
            )
            return await ctx.send(embed=embed)

        await self._embed_msg(ctx, _("Nothing playing."))