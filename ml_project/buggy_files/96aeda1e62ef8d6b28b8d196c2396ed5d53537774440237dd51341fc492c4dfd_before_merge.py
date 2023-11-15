    async def localblacklist_add(
        self, ctx: commands.Context, *, user_or_role: Union[discord.Member, discord.Role]
    ):
        """
        Adds a user or role to the blacklist.
        """
        user = isinstance(user_or_role, discord.Member)

        if user and await ctx.bot.is_owner(obj):
            await ctx.send(_("You cannot blacklist an owner!"))
            return

        async with ctx.bot.db.guild(ctx.guild).blacklist() as curr_list:
            if user_or_role.id not in curr_list:
                curr_list.append(user_or_role.id)

        if user:
            await ctx.send(_("User added to blacklist."))
        else:
            await ctx.send(_("Role added to blacklist."))