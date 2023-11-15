    async def whitelist_remove(self, ctx: commands.Context, *, user: Union[discord.Member, int]):
        """
        Removes user from whitelist.
        """
        removed = False
        uid = getattr(user, "id", user)
        async with ctx.bot._config.whitelist() as curr_list:
            if uid in curr_list:
                removed = True
                curr_list.remove(uid)

        if removed:
            await ctx.send(_("User has been removed from whitelist."))
        else:
            await ctx.send(_("User was not in the whitelist."))