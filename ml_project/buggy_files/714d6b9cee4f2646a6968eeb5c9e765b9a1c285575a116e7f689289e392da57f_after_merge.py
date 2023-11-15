    async def whitelist_remove(
        self, ctx: commands.Context, *users: List[Union[discord.Member, int]]
    ):
        """
        Removes user from whitelist.
        """
        uids = [getattr(user, "id", user) for user in users]
        await self.bot._whiteblacklist_cache.remove_from_whitelist(None, uids)

        await ctx.send(_("Users have been removed from whitelist."))