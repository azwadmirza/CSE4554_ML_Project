    async def dj(self, ctx: commands.Context):
        """Toggle DJ mode.

        DJ mode allows users with the DJ role to use audio commands.
        """
        dj_role = self._dj_role_cache.setdefault(
            ctx.guild.id, await self.config.guild(ctx.guild).dj_role()
        )
        dj_role = ctx.guild.get_role(dj_role)
        if dj_role is None:
            await self._embed_msg(
                ctx,
                title=_("Missing DJ Role"),
                description=_(
                    "Please set a role to use with DJ mode. Enter the role name or ID now."
                ),
            )

            try:
                pred = MessagePredicate.valid_role(ctx)
                await ctx.bot.wait_for("message", timeout=15.0, check=pred)
                await ctx.invoke(self.role, role_name=pred.result)
            except asyncio.TimeoutError:
                return await self._embed_msg(ctx, title=_("Response timed out, try again later."))
        dj_enabled = self._dj_status_cache.setdefault(
            ctx.guild.id, await self.config.guild(ctx.guild).dj_enabled()
        )
        await self.config.guild(ctx.guild).dj_enabled.set(not dj_enabled)
        self._dj_status_cache[ctx.guild.id] = not dj_enabled
        await self._embed_msg(
            ctx,
            title=_("Setting Changed"),
            description=_("DJ role: {true_or_false}.").format(
                true_or_false=_("Enabled") if not dj_enabled else _("Disabled")
            ),
        )