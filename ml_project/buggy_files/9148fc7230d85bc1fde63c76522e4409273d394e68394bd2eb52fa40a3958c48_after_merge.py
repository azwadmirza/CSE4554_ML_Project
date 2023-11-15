    async def wsport(self, ctx, ws_port: int):
        """Set the lavalink websocket server port."""
        await self.config.ws_port.set(ws_port)
        if await self._check_external():
            embed = discord.Embed(
                colour=await ctx.embed_colour(),
                title=_("Websocket port set to {port}.").format(port=ws_port),
            )
            embed.set_footer(text=_("External lavalink server set to True."))
            await ctx.send(embed=embed)
        else:
            await self._embed_msg(ctx, _("Websocket port set to {port}.").format(port=ws_port))