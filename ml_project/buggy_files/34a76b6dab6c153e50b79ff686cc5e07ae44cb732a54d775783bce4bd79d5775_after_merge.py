    async def bump(self, ctx: commands.Context, index: int):
        """Bump a track number to the top of the queue."""
        dj_enabled = self._dj_status_cache.setdefault(
            ctx.guild.id, await self.config.guild(ctx.guild).dj_enabled()
        )

        if not self._player_check(ctx):
            return await self._embed_msg(ctx, title=_("Nothing playing."))
        player = lavalink.get_player(ctx.guild.id)
        if (
            not ctx.author.voice or ctx.author.voice.channel != player.channel
        ) and not await self._can_instaskip(ctx, ctx.author):
            return await self._embed_msg(
                ctx,
                title=_("Unable To Bump Track"),
                description=_("You must be in the voice channel to bump a track."),
            )
        if dj_enabled:
            if not await self._can_instaskip(ctx, ctx.author):
                return await self._embed_msg(
                    ctx,
                    title=_("Unable To Bump Track"),
                    description=_("You need the DJ role to bump tracks."),
                )
        if index > len(player.queue) or index < 1:
            return await self._embed_msg(
                ctx,
                title=_("Unable To Bump Track"),
                description=_("Song number must be greater than 1 and within the queue limit."),
            )

        bump_index = index - 1
        bump_song = player.queue[bump_index]
        bump_song.extras["bumped"] = True
        player.queue.insert(0, bump_song)
        removed = player.queue.pop(index)
        description = get_track_description(removed)
        await self._embed_msg(
            ctx, title=_("Moved track to the top of the queue."), description=description
        )