    async def thumbnail(self, ctx):
        """Toggle displaying a thumbnail on audio messages."""
        thumbnail = await self.config.guild(ctx.guild).thumbnail()
        await self.config.guild(ctx.guild).thumbnail.set(not thumbnail)
        await self._embed_msg(
            ctx, _("Thumbnail display: {true_or_false}.").format(true_or_false=not thumbnail)
        )