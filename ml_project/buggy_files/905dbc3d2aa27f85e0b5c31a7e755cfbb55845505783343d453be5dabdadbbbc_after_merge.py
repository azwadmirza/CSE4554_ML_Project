    async def command_not_found(self, ctx, help_for):
        """
        Sends an error, fuzzy help, or stays quiet based on settings
        """
        coms = [c async for c in self.help_filter_func(ctx, ctx.bot.walk_commands())]
        fuzzy_commands = await fuzzy_command_search(ctx, help_for, commands=coms, min_score=75)
        use_embeds = await ctx.embed_requested()
        if fuzzy_commands:
            ret = await format_fuzzy_results(ctx, fuzzy_commands, embed=use_embeds)
            if use_embeds:
                ret.set_author(name=f"{ctx.me.display_name} Help Menu", icon_url=ctx.me.avatar_url)
                tagline = (await ctx.bot.db.help.tagline()) or self.get_default_tagline(ctx)
                ret.set_footer(text=tagline)
                await ctx.send(embed=ret)
            else:
                await ctx.send(ret)
        elif await ctx.bot.db.help.verify_exists():
            ret = T_("Help topic for *{command_name}* not found.").format(command_name=help_for)
            if use_embeds:
                ret = discord.Embed(color=(await ctx.embed_color()), description=ret)
                ret.set_author(name=f"{ctx.me.display_name} Help Menu", icon_url=ctx.me.avatar_url)
                tagline = (await ctx.bot.db.help.tagline()) or self.get_default_tagline(ctx)
                ret.set_footer(text=tagline)
                await ctx.send(embed=ret)
            else:
                await ctx.send(ret)