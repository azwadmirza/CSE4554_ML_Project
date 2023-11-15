    async def repeat(self, ctx: commands.Context):
        """Toggle repeat."""
        dj_enabled = await self.config.guild(ctx.guild).dj_enabled()
        if dj_enabled:
            if not await self._can_instaskip(ctx, ctx.author) and not await self._has_dj_role(
                ctx, ctx.author
            ):
                return await self._embed_msg(ctx, _("You need the DJ role to toggle repeat."))
        if self._player_check(ctx):
            await self._data_check(ctx)
            player = lavalink.get_player(ctx.guild.id)
            if (
                not ctx.author.voice or ctx.author.voice.channel != player.channel
            ) and not await self._can_instaskip(ctx, ctx.author):
                return await self._embed_msg(
                    ctx, _("You must be in the voice channel to toggle repeat.")
                )

        autoplay = await self.config.guild(ctx.guild).auto_play()
        repeat = await self.config.guild(ctx.guild).repeat()
        msg = ""
        msg += _("Repeat tracks: {true_or_false}.").format(
            true_or_false=_("Enabled") if not repeat else _("Disabled")
        )
        await self.config.guild(ctx.guild).repeat.set(not repeat)
        if repeat is not True and autoplay is True:
            msg += _("\nAuto-play has been disabled.")
            await self.config.guild(ctx.guild).auto_play.set(False)

        embed = discord.Embed(
            title=_("Repeat settings changed"), description=msg, colour=await ctx.embed_colour()
        )
        await ctx.send(embed=embed)
        if self._player_check(ctx):
            await self._data_check(ctx)