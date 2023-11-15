    async def whitelist_add(self, ctx, *, user: Union[discord.Member, int]):
        """
        Adds a user to the whitelist.
        """
        uid = getattr(user, "id", user)
        async with ctx.bot._config.whitelist() as curr_list:
            if uid not in curr_list:
                curr_list.append(uid)

        await ctx.send(_("User added to whitelist."))