    async def dj(self, ctx):
        """Toggle DJ mode.

        DJ mode allows users with the DJ role to use audio commands.
        """
        dj_role_id = await self.config.guild(ctx.guild).dj_role()
        if dj_role_id is None:
            await self._embed_msg(
                ctx, _("Please set a role to use with DJ mode. Enter the role name or ID now.")
            )

            try:
                pred = MessagePredicate.valid_role(ctx)
                await ctx.bot.wait_for("message", timeout=15.0, check=pred)
                await ctx.invoke(self.role, pred.result)
            except asyncio.TimeoutError:
                return await self._embed_msg(ctx, _("Response timed out, try again later."))

        dj_enabled = await self.config.guild(ctx.guild).dj_enabled()
        await self.config.guild(ctx.guild).dj_enabled.set(not dj_enabled)
        await self._embed_msg(
            ctx, _("DJ role enabled: {true_or_false}.").format(true_or_false=not dj_enabled)
        )