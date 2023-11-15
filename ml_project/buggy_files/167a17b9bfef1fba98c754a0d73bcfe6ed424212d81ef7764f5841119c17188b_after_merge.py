    async def blacklist_list(self, ctx: commands.Context):
        """
        Lists blacklisted users.
        """
        curr_list = await self.bot._whiteblacklist_cache.get_blacklist(None)

        if not curr_list:
            await ctx.send("Blacklist is empty.")
            return

        msg = _("Blacklisted Users:")
        for user in curr_list:
            msg += "\n\t- {}".format(user)

        for page in pagify(msg):
            await ctx.send(box(page))