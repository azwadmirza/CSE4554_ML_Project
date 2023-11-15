    async def blacklist_add(self, ctx: commands.Context, *, user: Union[discord.Member, int]):
        """
        Adds a user to the blacklist.
        """
        if await ctx.bot.is_owner(user):
            await ctx.send(_("You cannot blacklist an owner!"))
            return

        uid = getattr(user, "id", user)
        async with ctx.bot._config.blacklist() as curr_list:
            if uid not in curr_list:
                curr_list.append(uid)

        await ctx.send(_("User added to blacklist."))