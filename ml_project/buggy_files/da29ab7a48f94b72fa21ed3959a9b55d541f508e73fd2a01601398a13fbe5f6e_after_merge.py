    async def _autoplay_reset(self, ctx: commands.Context):
        """Resets auto-play to the default playlist."""
        playlist_data = dict(enabled=False, id=None, name=None, scope=None)
        await self.config.guild(ctx.guild).autoplaylist.set(playlist_data)
        return await self._embed_msg(
            ctx,
            title=_("Setting Changed"),
            description=_("Set auto-play playlist to default value."),
        )