    async def eq(self, ctx: commands.Context):
        """Equalizer management."""
        if not self._player_check(ctx):
            ctx.command.reset_cooldown(ctx)
            return await self._embed_msg(ctx, _("Nothing playing."))
        dj_enabled = await self.config.guild(ctx.guild).dj_enabled()
        player = lavalink.get_player(ctx.guild.id)
        eq = player.fetch("eq", Equalizer())
        reactions = ["◀", "⬅", "⏫", "🔼", "🔽", "⏬", "➡", "▶", "⏺", "ℹ"]
        await self._eq_msg_clear(player.fetch("eq_message"))
        eq_message = await ctx.send(box(eq.visualise(), lang="ini"))

        if dj_enabled and not await self._can_instaskip(ctx, ctx.author):
            try:
                await eq_message.add_reaction("ℹ")
            except discord.errors.NotFound:
                pass
        else:
            start_adding_reactions(eq_message, reactions, self.bot.loop)

        eq_msg_with_reacts = await ctx.fetch_message(eq_message.id)
        player.store("eq_message", eq_msg_with_reacts)
        await self._eq_interact(ctx, player, eq, eq_msg_with_reacts, 0)