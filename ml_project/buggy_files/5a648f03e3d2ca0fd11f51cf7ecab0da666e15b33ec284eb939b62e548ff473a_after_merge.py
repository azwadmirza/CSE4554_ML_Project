    async def emptydisconnect(self, ctx: commands.Context, seconds: int):
        """Auto-disconnect from channel when bot is alone in it for x seconds, 0 to disable."""
        if seconds < 0:
            return await self._embed_msg(
                ctx, title=_("Invalid Time"), description=_("Seconds can't be less than zero.")
            )
        if 10 > seconds > 0:
            seconds = 10
        if seconds == 0:
            enabled = False
            await self._embed_msg(
                ctx, title=_("Setting Changed"), description=_("Empty disconnect disabled.")
            )
        else:
            enabled = True
            await self._embed_msg(
                ctx,
                title=_("Setting Changed"),
                description=_("Empty disconnect timer set to {num_seconds}.").format(
                    num_seconds=dynamic_time(seconds)
                ),
            )

        await self.config.guild(ctx.guild).emptydc_timer.set(seconds)
        await self.config.guild(ctx.guild).emptydc_enabled.set(enabled)