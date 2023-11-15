    async def _eq_set(self, ctx: commands.Context, band_name_or_position, band_value: float):
        """Set an eq band with a band number or name and value.

        Band positions are 1-15 and values have a range of -0.25 to 1.0.
        Band names are 25, 40, 63, 100, 160, 250, 400, 630, 1k, 1.6k, 2.5k, 4k,
        6.3k, 10k, and 16k Hz.
        Setting a band value to -0.25 nullifies it while +0.25 is double.
        """
        if not self._player_check(ctx):
            return await self._embed_msg(ctx, _("Nothing playing."))

        dj_enabled = await self.config.guild(ctx.guild).dj_enabled()
        if dj_enabled:
            if not await self._can_instaskip(ctx, ctx.author):
                return await self._embed_msg(
                    ctx, _("You need the DJ role to set equalizer presets.")
                )

        player = lavalink.get_player(ctx.guild.id)
        band_names = [
            "25",
            "40",
            "63",
            "100",
            "160",
            "250",
            "400",
            "630",
            "1k",
            "1.6k",
            "2.5k",
            "4k",
            "6.3k",
            "10k",
            "16k",
        ]

        eq = player.fetch("eq", Equalizer())
        bands_num = eq._band_count
        if band_value > 1:
            band_value = 1
        elif band_value <= -0.25:
            band_value = -0.25
        else:
            band_value = round(band_value, 1)

        try:
            band_number = int(band_name_or_position) - 1
        except ValueError:
            band_number = None

        if band_number not in range(0, bands_num) and band_name_or_position not in band_names:
            return await self._embed_msg(
                ctx,
                _(
                    "Valid band numbers are 1-15 or the band names listed in "
                    "the help for this command."
                ),
            )

        if band_name_or_position in band_names:
            band_pos = band_names.index(band_name_or_position)
            band_int = False
            eq.set_gain(int(band_pos), band_value)
            await self._apply_gain(ctx.guild.id, int(band_pos), band_value)
        else:
            band_int = True
            eq.set_gain(band_number, band_value)
            await self._apply_gain(ctx.guild.id, band_number, band_value)

        await self._eq_msg_clear(player.fetch("eq_message"))
        await self.config.custom("EQUALIZER", ctx.guild.id).eq_bands.set(eq.bands)
        player.store("eq", eq)
        band_name = band_names[band_number] if band_int else band_name_or_position
        message = await ctx.send(
            content=box(eq.visualise(), lang="ini"),
            embed=discord.Embed(
                colour=await ctx.embed_colour(),
                title=_(
                    "The {band_name}Hz band has been set to {band_value}.".format(
                        band_name=band_name, band_value=band_value
                    )
                ),
            ),
        )
        player.store("eq_message", message)