    async def host(self, ctx: commands.Context, host: str):
        """Set the lavalink server host."""
        await self.config.host.set(host)
        footer = None
        if await self._check_external():
            footer = _("External lavalink server set to True.")
        await self._embed_msg(
            ctx,
            title=_("Setting Changed"),
            description=_("Host set to {host}.").format(host=host),
            footer=footer,
        )
        self._restart_connect()