    async def external(self, ctx: commands.Context):
        """Toggle using external lavalink servers."""
        external = await self.config.use_external_lavalink()
        await self.config.use_external_lavalink.set(not external)

        if external:
            embed = discord.Embed(
                colour=await ctx.embed_colour(),
                title=_("External lavalink server: {true_or_false}.").format(
                    true_or_false=_("Enabled") if not external else _("Disabled")
                ),
            )
            await ctx.send(embed=embed)
        else:
            if self._manager is not None:
                await self._manager.shutdown()
            await self._embed_msg(
                ctx,
                _("External lavalink server: {true_or_false}.").format(
                    true_or_false=_("Enabled") if not external else _("Disabled")
                ),
            )

        self._restart_connect()