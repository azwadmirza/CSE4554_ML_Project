    async def reorderpath(self, ctx: commands.Context, from_: int, to: int):
        """
        Reorders paths internally to allow discovery of different cogs.
        """
        # Doing this because in the paths command they're 1 indexed
        from_ -= 1
        to -= 1
        if from_ < 0 or to < 0:
            await ctx.send(_("Path numbers must be positive."))
            return

        all_paths = await ctx.bot.cog_mgr.user_defined_paths()
        try:
            to_move = all_paths.pop(from_)
        except IndexError:
            await ctx.send(_("Invalid 'from' index."))
            return

        try:
            all_paths.insert(to, to_move)
        except IndexError:
            await ctx.send(_("Invalid 'to' index."))
            return

        await ctx.bot.cog_mgr.set_paths(all_paths)
        await ctx.send(_("Paths reordered."))