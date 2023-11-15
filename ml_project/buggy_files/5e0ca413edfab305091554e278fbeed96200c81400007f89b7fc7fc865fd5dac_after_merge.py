    async def volume(self, ctx: commands.Context, vol: int = None):
        """Set the volume, 1% - 150%."""
        dj_enabled = self._dj_status_cache.setdefault(
            ctx.guild.id, await self.config.guild(ctx.guild).dj_enabled()
        )
        if not vol:
            vol = await self.config.guild(ctx.guild).volume()
            embed = discord.Embed(title=_("Current Volume:"), description=str(vol) + "%")
            if not self._player_check(ctx):
                embed.set_footer(text=_("Nothing playing."))
            return await self._embed_msg(ctx, embed=embed)
        if self._player_check(ctx):
            player = lavalink.get_player(ctx.guild.id)
            if (
                not ctx.author.voice or ctx.author.voice.channel != player.channel
            ) and not await self._can_instaskip(ctx, ctx.author):
                return await self._embed_msg(
                    ctx,
                    title=_("Unable To Change Volume"),
                    description=_("You must be in the voice channel to change the volume."),
                )
        if dj_enabled:
            if not await self._can_instaskip(ctx, ctx.author) and not await self._has_dj_role(
                ctx, ctx.author
            ):
                return await self._embed_msg(
                    ctx,
                    title=_("Unable To Change Volume"),
                    description=_("You need the DJ role to change the volume."),
                )
        if vol < 0:
            vol = 0
        if vol > 150:
            vol = 150
            await self.config.guild(ctx.guild).volume.set(vol)
            if self._player_check(ctx):
                await lavalink.get_player(ctx.guild.id).set_volume(vol)
        else:
            await self.config.guild(ctx.guild).volume.set(vol)
            if self._player_check(ctx):
                await lavalink.get_player(ctx.guild.id).set_volume(vol)
        embed = discord.Embed(title=_("Volume:"), description=str(vol) + "%")
        if not self._player_check(ctx):
            embed.set_footer(text=_("Nothing playing."))
        await self._embed_msg(ctx, embed=embed)