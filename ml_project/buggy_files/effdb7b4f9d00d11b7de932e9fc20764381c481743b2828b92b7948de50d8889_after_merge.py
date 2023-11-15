    async def _eq_reset(self, ctx: commands.Context):
        """Reset the eq to 0 across all bands."""
        if not self._player_check(ctx):
            return await self._embed_msg(ctx, title=_("Nothing playing."))
        dj_enabled = self._dj_status_cache.setdefault(
            ctx.guild.id, await self.config.guild(ctx.guild).dj_enabled()
        )
        if dj_enabled:
            if not await self._can_instaskip(ctx, ctx.author):
                return await self._embed_msg(
                    ctx,
                    title=_("Unable To Modify Preset"),
                    description=_("You need the DJ role to reset the equalizer."),
                )
        player = lavalink.get_player(ctx.guild.id)
        eq = player.fetch("eq", Equalizer())

        for band in range(eq._band_count):
            eq.set_gain(band, 0.0)

        await self._apply_gains(ctx.guild.id, eq.bands)
        await self.config.custom("EQUALIZER", ctx.guild.id).eq_bands.set(eq.bands)
        player.store("eq", eq)
        await self._eq_msg_clear(player.fetch("eq_message"))
        message = await ctx.send(
            content=box(eq.visualise(), lang="ini"),
            embed=discord.Embed(
                colour=await ctx.embed_colour(), title=_("Equalizer values have been reset.")
            ),
        )
        player.store("eq_message", message)