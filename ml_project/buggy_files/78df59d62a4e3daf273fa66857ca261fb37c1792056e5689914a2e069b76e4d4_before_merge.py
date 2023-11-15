    async def removepath(self, ctx: commands.Context, path_number: int):
        """
        Removes a path from the available cog paths given the path_number
            from !paths
        """
        path_number -= 1
        if path_number < 0:
            await ctx.send(_("Path numbers must be positive."))
            return

        cog_paths = await ctx.bot.cog_mgr.user_defined_paths()
        try:
            to_remove = cog_paths.pop(path_number)
        except IndexError:
            await ctx.send(_("That is an invalid path number."))
            return

        await ctx.bot.cog_mgr.remove_path(to_remove)
        await ctx.send(_("Path successfully removed."))