    async def password(self, ctx: commands.Context, password: str):
        """Set the lavalink server password."""
        await self.config.password.set(str(password))
        footer = None
        if await self._check_external():
            footer = _("External lavalink server set to True.")
        await self._embed_msg(
            ctx,
            title=_("Setting Changed"),
            description=_("Server password set to {password}.").format(password=password),
            footer=footer,
        )

        self._restart_connect()