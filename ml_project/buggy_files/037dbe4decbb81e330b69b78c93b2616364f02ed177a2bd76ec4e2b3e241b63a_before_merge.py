    async def thumbnail(self, ctx: commands.Context):
        """Toggle displaying a thumbnail on audio messages."""
        thumbnail = await self.config.guild(ctx.guild).thumbnail()
        await self.config.guild(ctx.guild).thumbnail.set(not thumbnail)
        await self._embed_msg(
            ctx,
            _("Thumbnail display: {true_or_false}.").format(
                true_or_false=_("Enabled") if not thumbnail else _("Disabled")
            ),
        )