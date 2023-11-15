    async def _eq_save(self, ctx: commands.Context, eq_preset: str = None):
        """Save the current eq settings to a preset."""
        if not self._player_check(ctx):
            return await self._embed_msg(ctx, _("Nothing playing."))
        dj_enabled = await self.config.guild(ctx.guild).dj_enabled()
        if dj_enabled:
            if not await self._can_instaskip(ctx, ctx.author):
                return await self._embed_msg(
                    ctx, _("You need the DJ role to save equalizer presets.")
                )
        if not eq_preset:
            await self._embed_msg(ctx, _("Please enter a name for this equalizer preset."))
            try:
                eq_name_msg = await ctx.bot.wait_for(
                    "message",
                    timeout=15.0,
                    check=MessagePredicate.regex(fr"^(?!{re.escape(ctx.prefix)})", ctx),
                )
                eq_preset = eq_name_msg.content.split(" ")[0].strip('"').lower()
            except asyncio.TimeoutError:
                return await self._embed_msg(
                    ctx, _("No equalizer preset name entered, try the command again later.")
                )

        eq_exists_msg = None
        eq_preset = eq_preset.lower().lstrip(ctx.prefix)
        eq_presets = await self.config.custom("EQUALIZER", ctx.guild.id).eq_presets()
        eq_list = list(eq_presets.keys())

        if len(eq_preset) > 20:
            return await self._embed_msg(ctx, _("Try the command again with a shorter name."))
        if eq_preset in eq_list:
            embed = discord.Embed(
                colour=await ctx.embed_colour(),
                title=_("Preset name already exists, do you want to replace it?"),
            )
            eq_exists_msg = await ctx.send(embed=embed)
            start_adding_reactions(eq_exists_msg, ReactionPredicate.YES_OR_NO_EMOJIS)
            pred = ReactionPredicate.yes_or_no(eq_exists_msg, ctx.author)
            await ctx.bot.wait_for("reaction_add", check=pred)
            if not pred.result:
                await self._clear_react(eq_exists_msg)
                embed2 = discord.Embed(
                    colour=await ctx.embed_colour(), title=_("Not saving preset.")
                )
                return await eq_exists_msg.edit(embed=embed2)

        player = lavalink.get_player(ctx.guild.id)
        eq = player.fetch("eq", Equalizer())
        to_append = {eq_preset: {"author": ctx.author.id, "bands": eq.bands}}
        new_eq_presets = {**eq_presets, **to_append}
        await self.config.custom("EQUALIZER", ctx.guild.id).eq_presets.set(new_eq_presets)
        embed3 = discord.Embed(
            colour=await ctx.embed_colour(),
            title=_(
                "Current equalizer saved to the {preset_name} preset.".format(
                    preset_name=eq_preset
                )
            ),
        )
        if eq_exists_msg:
            await self._clear_react(eq_exists_msg)
            await eq_exists_msg.edit(embed=embed3)
        else:
            await ctx.send(embed=embed3)