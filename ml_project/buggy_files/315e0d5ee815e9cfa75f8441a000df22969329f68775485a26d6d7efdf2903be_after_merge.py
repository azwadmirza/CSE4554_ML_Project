    async def pause(self, ctx: commands.Context):
        """Pause or resume a playing track."""
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
                title=_("Unable To Manage Tracks"),
                description=_("You must be in the voice channel to pause or resume."),
            )
        if dj_enabled:
            if not await self._can_instaskip(ctx, ctx.author) and not await self._is_alone(ctx):
                return await self._embed_msg(
                    ctx,
                    title=_("Unable To Manage Tracks"),
                    description=_("You need the DJ role to pause or resume tracks."),
                )

        if not player.current:
            return await self._embed_msg(ctx, title=_("Nothing playing."))
        description = get_track_description(player.current)

        if player.current and not player.paused:
            await player.pause()
            return await self._embed_msg(ctx, title=_("Track Paused"), description=description)
        if player.current and player.paused:
            await player.pause(False)
            return await self._embed_msg(ctx, title=_("Track Resumed"), description=description)

        await self._embed_msg(ctx, title=_("Nothing playing."))