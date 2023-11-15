    async def _autoplay_toggle(self, ctx: commands.Context):
        """Toggle auto-play when there no songs in queue."""
        autoplay = await self.config.guild(ctx.guild).auto_play()
        repeat = await self.config.guild(ctx.guild).repeat()
        disconnect = await self.config.guild(ctx.guild).disconnect()
        msg = _("Auto-play when queue ends: {true_or_false}.").format(
            true_or_false=_("Enabled") if not autoplay else _("Disabled")
        )
        await self.config.guild(ctx.guild).auto_play.set(not autoplay)
        if autoplay is not True and repeat is True:
            msg += _("\nRepeat has been disabled.")
            await self.config.guild(ctx.guild).repeat.set(False)
        if autoplay is not True and disconnect is True:
            msg += _("\nAuto-disconnecting at queue end has been disabled.")
            await self.config.guild(ctx.guild).disconnect.set(False)

        await self._embed_msg(ctx, title=_("Setting Changed"), description=msg)
        if self._player_check(ctx):
            await self._data_check(ctx)