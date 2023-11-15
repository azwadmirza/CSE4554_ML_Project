    async def password(self, ctx: commands.Context, password: str):
        """Set the lavalink server password."""
        await self.config.password.set(str(password))
        if await self._check_external():
            embed = discord.Embed(
                colour=await ctx.embed_colour(),
                title=_("Server password set to {password}.").format(password=password),
            )
            embed.set_footer(text=_("External lavalink server set to True."))
            await ctx.send(embed=embed)
        else:
            await self._embed_msg(
                ctx, _("Server password set to {password}.").format(password=password)
            )

        self._restart_connect()