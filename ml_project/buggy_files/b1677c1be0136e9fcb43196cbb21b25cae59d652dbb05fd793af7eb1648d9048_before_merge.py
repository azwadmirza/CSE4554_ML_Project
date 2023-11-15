    async def restport(self, ctx: commands.Context, rest_port: int):
        """Set the lavalink REST server port."""
        await self.config.rest_port.set(rest_port)
        if await self._check_external():
            embed = discord.Embed(
                colour=await ctx.embed_colour(),
                title=_("REST port set to {port}.").format(port=rest_port),
            )
            embed.set_footer(text=_("External lavalink server set to True."))
            await ctx.send(embed=embed)
        else:
            await self._embed_msg(ctx, _("REST port set to {port}.").format(port=rest_port))

        self._restart_connect()