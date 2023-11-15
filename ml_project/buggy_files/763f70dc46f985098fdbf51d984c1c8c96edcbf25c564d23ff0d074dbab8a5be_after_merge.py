    async def _eq_list(self, ctx: commands.Context):
        """List saved eq presets."""
        eq_presets = await self.config.custom("EQUALIZER", ctx.guild.id).eq_presets()
        if not eq_presets.keys():
            return await self._embed_msg(ctx, title=_("No saved equalizer presets."))

        space = "\N{EN SPACE}"
        header_name = _("Preset Name")
        header_author = _("Author")
        header = box(
            "[{header_name}]{space}[{header_author}]\n".format(
                header_name=header_name, space=space * 9, header_author=header_author
            ),
            lang="ini",
        )
        preset_list = ""
        for preset, bands in eq_presets.items():
            try:
                author = self.bot.get_user(bands["author"])
            except TypeError:
                author = "None"
            msg = f"{preset}{space * (22 - len(preset))}{author}\n"
            preset_list += msg

        page_list = []
        colour = await ctx.embed_colour()
        for page in pagify(preset_list, delims=[", "], page_length=1000):
            formatted_page = box(page, lang="ini")
            embed = discord.Embed(colour=colour, description=f"{header}\n{formatted_page}")
            embed.set_footer(
                text=_("{num} preset(s)").format(num=humanize_number(len(list(eq_presets.keys()))))
            )
            page_list.append(embed)
        await menu(ctx, page_list, DEFAULT_CONTROLS)