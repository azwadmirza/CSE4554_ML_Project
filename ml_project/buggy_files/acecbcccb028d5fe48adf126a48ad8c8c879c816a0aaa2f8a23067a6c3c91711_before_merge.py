    async def localwhitelist_list(self, ctx: commands.Context):
        """
        Lists whitelisted users and roles.
        """
        curr_list = await ctx.bot._config.guild(ctx.guild).whitelist()

        if not curr_list:
            await ctx.send("Local whitelist is empty.")
            return

        msg = _("Whitelisted Users and roles:")
        for obj in curr_list:
            msg += "\n\t- {}".format(obj)

        for page in pagify(msg):
            await ctx.send(box(page))