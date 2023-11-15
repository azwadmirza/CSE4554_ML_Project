    async def vote(self, ctx: commands.Context, percent: int):
        """Percentage needed for non-mods to skip tracks. 0 to disable."""
        if percent < 0:
            return await self._embed_msg(ctx, _("Can't be less than zero."))
        elif percent > 100:
            percent = 100
        if percent == 0:
            enabled = False
            await self._embed_msg(
                ctx, _("Voting disabled. All users can use queue management commands.")
            )
        else:
            enabled = True
            await self._embed_msg(
                ctx, _("Vote percentage set to {percent}%.").format(percent=percent)
            )

        await self.config.guild(ctx.guild).vote_percent.set(percent)
        await self.config.guild(ctx.guild).vote_enabled.set(enabled)