    async def _set(self, ctx):
        """Changes Red's settings"""
        if ctx.invoked_subcommand is None:
            if ctx.guild:
                admin_role_id = await ctx.bot.db.guild(ctx.guild).admin_role()
                admin_role = discord.utils.get(ctx.guild.roles, id=admin_role_id) or "Not set"
                mod_role_id = await ctx.bot.db.guild(ctx.guild).mod_role()
                mod_role = discord.utils.get(ctx.guild.roles, id=mod_role_id) or "Not set"
                prefixes = await ctx.bot.db.guild(ctx.guild).prefix()
                guild_settings = f"Admin role: {admin_role}\nMod role: {mod_role}\n"
            else:
                guild_settings = ""
            if not prefixes:
                prefixes = await ctx.bot.db.prefix()
            locale = await ctx.bot.db.locale()

            prefix_string = " ".join(prefixes)
            settings = (
                f"{ctx.bot.user.name} Settings:\n\n"
                f"Prefixes: {prefix_string}\n"
                f"{guild_settings}"
                f"Locale: {locale}"
            )
            await ctx.send(box(settings))
            await ctx.send_help()