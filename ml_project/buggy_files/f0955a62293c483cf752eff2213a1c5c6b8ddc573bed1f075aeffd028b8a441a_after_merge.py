    async def blacklist_add(self, ctx: commands.Context, *users: List[Union[discord.Member, int]]):
        """
        Adds a user to the blacklist.
        """
        for user in users:
            if isinstance(user, int):
                user_obj = discord.Object(id=user)
            else:
                user_obj = user
            if await ctx.bot.is_owner(user_obj):
                await ctx.send(_("You cannot blacklist an owner!"))
                return

        uids = [getattr(user, "id", user) for user in users]
        await self.bot._whiteblacklist_cache.add_to_blacklist(None, uids)

        await ctx.send(_("User added to blacklist."))