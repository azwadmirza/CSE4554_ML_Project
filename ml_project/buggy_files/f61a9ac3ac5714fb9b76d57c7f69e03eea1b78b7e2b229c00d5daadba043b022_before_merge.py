    async def localwhitelist_remove(
        self, ctx: commands.Context, *, user_or_role: Union[discord.Member, discord.Role, int]
    ):
        """
        Removes user or role from whitelist.
        """
        user = isinstance(user_or_role, discord.Member)
        if isinstance(user_or_role, int):
            user_or_role = discord.Object(id=user_or_role)
            user = True

        removed = False
        async with ctx.bot._config.guild(ctx.guild).whitelist() as curr_list:
            if user_or_role.id in curr_list:
                removed = True
                curr_list.remove(user_or_role.id)

        if removed:
            if user:
                await ctx.send(_("User has been removed from whitelist."))
            else:
                await ctx.send(_("Role has been removed from whitelist."))
        else:
            if user:
                await ctx.send(_("User was not in the whitelist."))
            else:
                await ctx.send(_("Role was not in the whitelist."))