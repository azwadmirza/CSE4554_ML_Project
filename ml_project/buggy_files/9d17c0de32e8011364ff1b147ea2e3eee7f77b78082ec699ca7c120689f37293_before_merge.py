    async def _queue_cleanself(self, ctx: commands.Context):
        """Removes all tracks you requested from the queue."""

        try:
            player = lavalink.get_player(ctx.guild.id)
        except KeyError:
            return await self._embed_msg(ctx, _("There's nothing in the queue."))
        if not self._player_check(ctx) or not player.queue:
            return await self._embed_msg(ctx, _("There's nothing in the queue."))

        clean_tracks = []
        removed_tracks = 0
        for track in player.queue:
            if track.requester != ctx.author:
                clean_tracks.append(track)
            else:
                removed_tracks += 1
        player.queue = clean_tracks
        if removed_tracks == 0:
            await self._embed_msg(ctx, _("Removed 0 tracks."))
        else:
            await self._embed_msg(
                ctx,
                _("Removed {removed_tracks} tracks queued by {member.display_name}.").format(
                    removed_tracks=removed_tracks, member=ctx.author
                ),
            )