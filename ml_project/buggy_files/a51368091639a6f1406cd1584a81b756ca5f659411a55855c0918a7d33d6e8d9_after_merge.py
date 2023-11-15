    async def help_filter_func(
        self, ctx, objects: Iterable[SupportsCanSee], bypass_hidden=False
    ) -> AsyncIterator[SupportsCanSee]:
        """
        This does most of actual filtering.
        """

        show_hidden = bypass_hidden or await ctx.bot.db.help.show_hidden()
        verify_checks = await ctx.bot.db.help.verify_checks()

        # TODO: Settings for this in core bot db
        for obj in objects:
            if verify_checks and not show_hidden:
                # Default Red behavior, can_see includes a can_run check.
                if await obj.can_see(ctx):
                    yield obj
            elif verify_checks:
                try:
                    can_run = await obj.can_run(ctx)
                except discord.DiscordException:
                    can_run = False
                if can_run:
                    yield obj
            elif not show_hidden:
                if not getattr(obj, "hidden", False):  # Cog compatibility
                    yield obj
            else:
                yield obj