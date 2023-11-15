    async def _set(self, ctx):
        """Changes Red's settings"""
        if ctx.invoked_subcommand is None:
            admin_role_id = await ctx.bot.db.guild(ctx.guild).admin_role()
            admin_role = discord.utils.get(ctx.guild.roles, id=admin_role_id)
            mod_role_id = await ctx.bot.db.guild(ctx.guild).mod_role()
            mod_role = discord.utils.get(ctx.guild.roles, id=mod_role_id)
            prefixes = await ctx.bot.db.guild(ctx.guild).prefix()
            if not prefixes:
                prefixes = await ctx.bot.db.prefix()
            locale = await ctx.bot.db.locale()

            settings = (
                "{} Settings:\n\n"
                "Prefixes: {}\n"
                "Admin role: {}\n"
                "Mod role: {}\n"
                "Locale: {}"
                "".format(
                    ctx.bot.user.name,
                    " ".join(prefixes),
                    admin_role.name if admin_role else "Not set",
                    mod_role.name if mod_role else "Not set",
                    locale,
                )
            )
            await ctx.send(box(settings))
            await ctx.send_help()