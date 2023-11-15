    async def dc(self, ctx: commands.Context):
        """Toggle the bot auto-disconnecting when done playing.

        This setting takes precedence over [p]audioset emptydisconnect.
        """

        disconnect = await self.config.guild(ctx.guild).disconnect()
        autoplay = await self.config.guild(ctx.guild).auto_play()
        msg = ""
        msg += _("Auto-disconnection at queue end: {true_or_false}.").format(
            true_or_false=_("Enabled") if not disconnect else _("Disabled")
        )
        await self.config.guild(ctx.guild).repeat.set(not disconnect)
        if disconnect is not True and autoplay is True:
            msg += _("\nAuto-play has been disabled.")
            await self.config.guild(ctx.guild).auto_play.set(False)

        await self.config.guild(ctx.guild).disconnect.set(not disconnect)

        embed = discord.Embed(
            title=_("Auto-disconnection settings changed"),
            description=msg,
            colour=await ctx.embed_colour(),
        )
        await ctx.send(embed=embed)