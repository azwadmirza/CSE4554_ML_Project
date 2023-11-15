    async def _eq_load(self, ctx: commands.Context, eq_preset: str):
        """Load a saved eq preset."""
        eq_preset = eq_preset.lower()
        eq_presets = await self.config.custom("EQUALIZER", ctx.guild.id).eq_presets()
        try:
            eq_values = eq_presets[eq_preset]["bands"]
        except KeyError:
            return await self._embed_msg(
                ctx, _("No preset named {eq_preset}.".format(eq_preset=eq_preset))
            )
        except TypeError:
            eq_values = eq_presets[eq_preset]

        if not self._player_check(ctx):
            return await self._embed_msg(ctx, _("Nothing playing."))

        dj_enabled = await self.config.guild(ctx.guild).dj_enabled()
        player = lavalink.get_player(ctx.guild.id)
        if dj_enabled:
            if not await self._can_instaskip(ctx, ctx.author):
                return await self._embed_msg(
                    ctx, _("You need the DJ role to load equalizer presets.")
                )

        await self.config.custom("EQUALIZER", ctx.guild.id).eq_bands.set(eq_values)
        await self._eq_check(ctx, player)
        eq = player.fetch("eq", Equalizer())
        await self._eq_msg_clear(player.fetch("eq_message"))
        message = await ctx.send(
            content=box(eq.visualise(), lang="ini"),
            embed=discord.Embed(
                colour=await ctx.embed_colour(),
                title=_("The {eq_preset} preset was loaded.".format(eq_preset=eq_preset)),
            ),
        )
        player.store("eq_message", message)