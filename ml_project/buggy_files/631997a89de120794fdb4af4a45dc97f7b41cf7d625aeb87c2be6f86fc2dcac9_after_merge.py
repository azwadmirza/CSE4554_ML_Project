    async def subcommand_not_found(self, ctx, command, not_found):
        """
        Sends an error
        """
        ret = T_("Command *{command_name}* has no subcommand named *{not_found}*.").format(
            command_name=command.qualified_name, not_found=not_found[0]
        )
        if await ctx.embed_requested():
            ret = discord.Embed(color=(await ctx.embed_color()), description=ret)
            ret.set_author(name=f"{ctx.me.display_name} Help Menu", icon_url=ctx.me.avatar_url)
            tagline = (await ctx.bot.db.help.tagline()) or self.get_default_tagline(ctx)
            ret.set_footer(text=tagline)
            await ctx.send(embed=ret)
        else:
            await ctx.send(ret)