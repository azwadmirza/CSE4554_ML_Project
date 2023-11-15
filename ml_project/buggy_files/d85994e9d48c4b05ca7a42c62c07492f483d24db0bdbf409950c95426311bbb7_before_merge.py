    async def cog_before_invoke(self, ctx: commands.Context):
        await self._ready_event.wait()
        # check for unsupported arch
        # Check on this needs refactoring at a later date
        # so that we have a better way to handle the tasks
        if self.llsetup in [ctx.command, ctx.command.root_parent]:
            pass

        elif self._connect_task and self._connect_task.cancelled():
            await ctx.send(
                "You have attempted to run Audio's Lavalink server on an unsupported"
                " architecture. Only settings related commands will be available."
            )
            raise RuntimeError(
                "Not running audio command due to invalid machine architecture for Lavalink."
            )

        dj_enabled = await self.config.guild(ctx.guild).dj_enabled()
        if dj_enabled:
            dj_role_obj = ctx.guild.get_role(await self.config.guild(ctx.guild).dj_role())
            if not dj_role_obj:
                await self.config.guild(ctx.guild).dj_enabled.set(None)
                await self.config.guild(ctx.guild).dj_role.set(None)
                await self._embed_msg(ctx, _("No DJ role found. Disabling DJ mode."))