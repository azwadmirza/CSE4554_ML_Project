    async def restport(self, ctx: commands.Context, rest_port: int):
        """Set the lavalink REST server port."""
        await self.config.rest_port.set(rest_port)
        footer = None
        if await self._check_external():
            footer = _("External lavalink server set to True.")
        await self._embed_msg(
            ctx,
            title=_("Setting Changed"),
            description=_("REST port set to {port}.").format(port=rest_port),
            footer=footer,
        )

        self._restart_connect()