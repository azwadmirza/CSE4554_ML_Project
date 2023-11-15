    async def remove(self, ctx: commands.Context, index: int):
        """Remove a specific track number from the queue."""
        dj_enabled = self._dj_status_cache.setdefault(
            ctx.guild.id, await self.config.guild(ctx.guild).dj_enabled()
        )
        if not self._player_check(ctx):
            return await self._embed_msg(ctx, title=_("Nothing playing."))
        player = lavalink.get_player(ctx.guild.id)
        if not player.queue:
            return await self._embed_msg(ctx, title=_("Nothing queued."))
        if dj_enabled:
            if not await self._can_instaskip(ctx, ctx.author):
                return await self._embed_msg(
                    ctx,
                    title=_("Unable To Modify Queue"),
                    description=_("You need the DJ role to remove tracks."),
                )
        if (
            not ctx.author.voice or ctx.author.voice.channel != player.channel
        ) and not await self._can_instaskip(ctx, ctx.author):
            return await self._embed_msg(
                ctx,
                title=_("Unable To Modify Queue"),
                description=_("You must be in the voice channel to manage the queue."),
            )
        if index > len(player.queue) or index < 1:
            return await self._embed_msg(
                ctx,
                title=_("Unable To Modify Queue"),
                description=_("Song number must be greater than 1 and within the queue limit."),
            )
        index -= 1
        removed = player.queue.pop(index)
        removed_title = get_track_description(removed)
        await self._embed_msg(
            ctx,
            title=_("Removed track from queue"),
            description=_("Removed {track} from the queue.").format(track=removed_title),
        )