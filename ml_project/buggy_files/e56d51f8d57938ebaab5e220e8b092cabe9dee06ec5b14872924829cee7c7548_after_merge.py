    async def whitelist_add(self, ctx: commands.Context, *users: List[Union[discord.Member, int]]):
        """
        Adds a user to the whitelist.
        """
        uids = [getattr(user, "id", user) for user in users]
        await self.bot._whiteblacklist_cache.add_to_whitelist(None, uids)

        await ctx.send(_("Users added to whitelist."))