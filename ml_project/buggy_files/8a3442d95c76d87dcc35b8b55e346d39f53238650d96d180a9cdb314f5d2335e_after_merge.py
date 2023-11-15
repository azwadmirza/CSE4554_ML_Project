    async def shuffle(self, ctx: commands.Context):
        """Toggle shuffle."""
        if ctx.invoked_subcommand is None:
            dj_enabled = self._dj_status_cache.setdefault(
                ctx.guild.id, await self.config.guild(ctx.guild).dj_enabled()
            )
            if dj_enabled:
                if not await self._can_instaskip(ctx, ctx.author):
                    return await self._embed_msg(
                        ctx,
                        title=_("Unable To Toggle Shuffle"),
                        description=_("You need the DJ role to toggle shuffle."),
                    )
            if self._player_check(ctx):
                await self._data_check(ctx)
                player = lavalink.get_player(ctx.guild.id)
                if (
                    not ctx.author.voice or ctx.author.voice.channel != player.channel
                ) and not await self._can_instaskip(ctx, ctx.author):
                    return await self._embed_msg(
                        ctx,
                        title=_("Unable To Toggle Shuffle"),
                        description=_("You must be in the voice channel to toggle shuffle."),
                    )

            shuffle = await self.config.guild(ctx.guild).shuffle()
            await self.config.guild(ctx.guild).shuffle.set(not shuffle)
            await self._embed_msg(
                ctx,
                title=_("Setting Changed"),
                description=_("Shuffle tracks: {true_or_false}.").format(
                    true_or_false=_("Enabled") if not shuffle else _("Disabled")
                ),
            )
            if self._player_check(ctx):
                await self._data_check(ctx)