    async def localwhitelist_add(
        self, ctx: commands.Context, *, user_or_role: Union[discord.Member, discord.Role, int]
    ):
        """
        Adds a user or role to the whitelist.
        """
        user = isinstance(user_or_role, discord.Member)
        if isinstance(user_or_role, int):
            user_or_role = discord.Object(id=user_or_role)
            user = True

        async with ctx.bot._config.guild(ctx.guild).whitelist() as curr_list:
            if user_or_role.id not in curr_list:
                curr_list.append(user_or_role.id)

        if user:
            await ctx.send(_("User added to whitelist."))
        else:
            await ctx.send(_("Role added to whitelist."))