    async def help_filter_func(
        self, ctx, objects: Iterable[SupportsCanSee], bypass_hidden=False
    ) -> AsyncIterator[SupportsCanSee]:
        """
        This does most of actual filtering.
        """
        # TODO: Settings for this in core bot db
        for obj in objects:
            if self.VERIFY_CHECKS and not (self.SHOW_HIDDEN or bypass_hidden):
                # Default Red behavior, can_see includes a can_run check.
                if await obj.can_see(ctx):
                    yield obj
            elif self.VERIFY_CHECKS:
                if await obj.can_run(ctx):
                    yield obj
            elif not (self.SHOW_HIDDEN or bypass_hidden):
                if getattr(obj, "hidden", False):  # Cog compatibility
                    yield obj
            else:
                yield obj