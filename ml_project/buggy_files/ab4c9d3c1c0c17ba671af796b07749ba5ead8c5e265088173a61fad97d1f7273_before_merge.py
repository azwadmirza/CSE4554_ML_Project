    async def localblacklist_list(self, ctx: commands.Context):
        """
        Lists blacklisted users and roles.
        """
        curr_list = await ctx.bot._config.guild(ctx.guild).blacklist()

        if not curr_list:
            await ctx.send("Local blacklist is empty.")
            return

        msg = _("Blacklisted Users and Roles:")
        for obj in curr_list:
            msg += "\n\t- {}".format(obj)

        for page in pagify(msg):
            await ctx.send(box(page))