    async def notify(self, ctx: commands.Context):
        """Toggle track announcement and other bot messages."""
        notify = await self.config.guild(ctx.guild).notify()
        await self.config.guild(ctx.guild).notify.set(not notify)
        await self._embed_msg(
            ctx,
            title=_("Setting Changed"),
            description=_("Notify mode: {true_or_false}.").format(
                true_or_false=_("Enabled") if not notify else _("Disabled")
            ),
        )