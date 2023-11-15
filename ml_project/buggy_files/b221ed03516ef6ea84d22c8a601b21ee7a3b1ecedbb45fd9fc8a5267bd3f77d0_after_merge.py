    async def wsport(self, ctx: commands.Context, ws_port: int):
        """Set the lavalink websocket server port."""
        await self.config.ws_port.set(ws_port)
        footer = None
        if await self._check_external():
            footer = _("External lavalink server set to True.")
        await self._embed_msg(
            ctx,
            title=_("Setting Changed"),
            description=_("Websocket port set to {port}.").format(port=ws_port),
            footer=footer,
        )

        self._restart_connect()