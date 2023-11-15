    async def bump(self, ctx: commands.Context, index: int):
        """Bump a track number to the top of the queue."""
        dj_enabled = await self.config.guild(ctx.guild).dj_enabled()
        if not self._player_check(ctx):
            return await self._embed_msg(ctx, _("Nothing playing."))
        player = lavalink.get_player(ctx.guild.id)
        if (
            not ctx.author.voice or ctx.author.voice.channel != player.channel
        ) and not await self._can_instaskip(ctx, ctx.author):
            return await self._embed_msg(
                ctx, _("You must be in the voice channel to bump a track.")
            )
        if dj_enabled:
            if not await self._can_instaskip(ctx, ctx.author):
                return await self._embed_msg(ctx, _("You need the DJ role to bump tracks."))
        if index > len(player.queue) or index < 1:
            return await self._embed_msg(
                ctx, _("Song number must be greater than 1 and within the queue limit.")
            )

        bump_index = index - 1
        bump_song = player.queue[bump_index]
        player.queue.insert(0, bump_song)
        removed = player.queue.pop(index)
        query = audio_dataclasses.Query.process_input(removed.uri)
        if query.is_local:
            localtrack = audio_dataclasses.LocalPath(removed.uri)
            if removed.title != "Unknown title":
                description = "**{} - {}**\n{}".format(
                    removed.author, removed.title, localtrack.to_string_hidden()
                )
            else:
                description = localtrack.to_string_hidden()
        else:
            description = "**[{}]({})**".format(removed.title, removed.uri)
        await ctx.send(
            embed=discord.Embed(
                title=_("Moved track to the top of the queue."),
                colour=await ctx.embed_colour(),
                description=description,
            )
        )