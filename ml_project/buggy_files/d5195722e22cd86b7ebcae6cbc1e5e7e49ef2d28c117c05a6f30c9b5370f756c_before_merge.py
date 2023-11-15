    async def remove(self, ctx: commands.Context, index: int):
        """Remove a specific track number from the queue."""
        dj_enabled = await self.config.guild(ctx.guild).dj_enabled()
        if not self._player_check(ctx):
            return await self._embed_msg(ctx, _("Nothing playing."))
        player = lavalink.get_player(ctx.guild.id)
        if not player.queue:
            return await self._embed_msg(ctx, _("Nothing queued."))
        if dj_enabled:
            if not await self._can_instaskip(ctx, ctx.author):
                return await self._embed_msg(ctx, _("You need the DJ role to remove tracks."))
        if (
            not ctx.author.voice or ctx.author.voice.channel != player.channel
        ) and not await self._can_instaskip(ctx, ctx.author):
            return await self._embed_msg(
                ctx, _("You must be in the voice channel to manage the queue.")
            )
        if index > len(player.queue) or index < 1:
            return await self._embed_msg(
                ctx, _("Song number must be greater than 1 and within the queue limit.")
            )
        index -= 1
        removed = player.queue.pop(index)
        query = audio_dataclasses.Query.process_input(removed.uri)
        if query.is_local:
            local_path = audio_dataclasses.LocalPath(removed.uri).to_string_hidden()
            if removed.title == "Unknown title":
                removed_title = local_path
            else:
                removed_title = "{} - {}\n{}".format(removed.author, removed.title, local_path)
        else:
            removed_title = removed.title
        await self._embed_msg(
            ctx, _("Removed {track} from the queue.").format(track=removed_title)
        )