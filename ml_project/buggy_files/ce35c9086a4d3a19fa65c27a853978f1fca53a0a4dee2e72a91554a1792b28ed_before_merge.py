    async def disconnect(self, ctx: commands.Context):
        """Disconnect from the voice channel."""
        if not self._player_check(ctx):
            return await self._embed_msg(ctx, _("Nothing playing."))
        else:
            dj_enabled = await self.config.guild(ctx.guild).dj_enabled()
            player = lavalink.get_player(ctx.guild.id)

            if dj_enabled:
                if not await self._can_instaskip(ctx, ctx.author):
                    return await self._embed_msg(ctx, _("You need the DJ role to disconnect."))
            if not await self._can_instaskip(ctx, ctx.author) and not await self._is_alone(ctx):
                return await self._embed_msg(ctx, _("There are other people listening to music."))
            else:
                await self._embed_msg(ctx, _("Disconnecting..."))
                self.bot.dispatch("red_audio_audio_disconnect", ctx.guild)
                self._play_lock(ctx, False)
                eq = player.fetch("eq")
                player.queue = []
                player.store("playing_song", None)
                if eq:
                    await self.config.custom("EQUALIZER", ctx.guild.id).eq_bands.set(eq.bands)
                await player.stop()
                await player.disconnect()