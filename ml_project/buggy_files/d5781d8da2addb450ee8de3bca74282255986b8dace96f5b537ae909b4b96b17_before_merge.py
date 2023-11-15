    async def host(self, ctx: commands.Context, host: str):
        """Set the lavalink server host."""
        await self.config.host.set(host)
        if await self._check_external():
            embed = discord.Embed(
                colour=await ctx.embed_colour(), title=_("Host set to {host}.").format(host=host)
            )
            embed.set_footer(text=_("External lavalink server set to True."))
            await ctx.send(embed=embed)
        else:
            await self._embed_msg(ctx, _("Host set to {host}.").format(host=host))

        self._restart_connect()