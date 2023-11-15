    async def emptypause(self, ctx: commands.Context, seconds: int):
        """Auto-pause after x seconds when room is empty, 0 to disable."""
        if seconds < 0:
            return await self._embed_msg(
                ctx, title=_("Invalid Time"), description=_("Seconds can't be less than zero.")
            )
        if 10 > seconds > 0:
            seconds = 10
        if seconds == 0:
            enabled = False
            await self._embed_msg(
                ctx, title=_("Setting Changed"), description=_("Empty pause disabled.")
            )
        else:
            enabled = True
            await self._embed_msg(
                ctx,
                title=_("Setting Changed"),
                description=_("Empty pause timer set to {num_seconds}.").format(
                    num_seconds=dynamic_time(seconds)
                ),
            )
        await self.config.guild(ctx.guild).emptypause_timer.set(seconds)
        await self.config.guild(ctx.guild).emptypause_enabled.set(enabled)