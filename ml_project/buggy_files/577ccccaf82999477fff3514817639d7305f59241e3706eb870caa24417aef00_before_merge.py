    async def status(self, ctx: commands.Context):
        """Enable/disable tracks' titles as status."""
        status = await self.config.status()
        await self.config.status.set(not status)
        await self._embed_msg(
            ctx,
            _("Song titles as status: {true_or_false}.").format(
                true_or_false=_("Enabled") if not status else _("Disabled")
            ),
        )