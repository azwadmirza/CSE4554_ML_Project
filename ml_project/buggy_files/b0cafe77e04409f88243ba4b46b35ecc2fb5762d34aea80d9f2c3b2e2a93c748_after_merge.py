    async def eq(self, ctx: commands.Context):
        """Equalizer management."""
        if not self._player_check(ctx):
            ctx.command.reset_cooldown(ctx)
            return await self._embed_msg(ctx, title=_("Nothing playing."))
        dj_enabled = self._dj_status_cache.setdefault(
            ctx.guild.id, await self.config.guild(ctx.guild).dj_enabled()
        )
        player = lavalink.get_player(ctx.guild.id)
        eq = player.fetch("eq", Equalizer())
        reactions = [
            "\N{BLACK LEFT-POINTING TRIANGLE}",
            "\N{LEFTWARDS BLACK ARROW}",
            "\N{BLACK UP-POINTING DOUBLE TRIANGLE}",
            "\N{UP-POINTING SMALL RED TRIANGLE}",
            "\N{DOWN-POINTING SMALL RED TRIANGLE}",
            "\N{BLACK DOWN-POINTING DOUBLE TRIANGLE}",
            "\N{BLACK RIGHTWARDS ARROW}",
            "\N{BLACK RIGHT-POINTING TRIANGLE}",
            "\N{BLACK CIRCLE FOR RECORD}",
            "\N{INFORMATION SOURCE}",
        ]
        await self._eq_msg_clear(player.fetch("eq_message"))
        eq_message = await ctx.send(box(eq.visualise(), lang="ini"))

        if dj_enabled and not await self._can_instaskip(ctx, ctx.author):
            with contextlib.suppress(discord.HTTPException):
                await eq_message.add_reaction("\N{INFORMATION SOURCE}")
        else:
            start_adding_reactions(eq_message, reactions, self.bot.loop)

        eq_msg_with_reacts = await ctx.fetch_message(eq_message.id)
        player.store("eq_message", eq_msg_with_reacts)
        await self._eq_interact(ctx, player, eq, eq_msg_with_reacts, 0)