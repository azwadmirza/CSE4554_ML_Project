    async def localblacklist_list(self, ctx: commands.Context):
        """
        Lists blacklisted users and roles.
        """
        curr_list = await self.bot._whiteblacklist_cache.get_blacklist(ctx.guild)

        if not curr_list:
            await ctx.send("Local blacklist is empty.")
            return

        msg = _("Blacklisted Users and Roles:")
        for obj in curr_list:
            msg += "\n\t- {}".format(obj)

        for page in pagify(msg):
            await ctx.send(box(page))