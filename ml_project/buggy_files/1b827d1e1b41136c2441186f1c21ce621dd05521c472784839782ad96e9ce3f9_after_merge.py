    async def maxlength(self, ctx: commands.Context, seconds: Union[int, str]):
        """Max length of a track to queue in seconds, 0 to disable.

        Accepts seconds or a value formatted like 00:00:00 (`hh:mm:ss`) or 00:00 (`mm:ss`). Invalid
        input will turn the max length setting off.
        """
        if not isinstance(seconds, int):
            seconds = time_convert(seconds)
        if seconds < 0:
            return await self._embed_msg(
                ctx, title=_("Invalid length"), description=_("Length can't be less than zero.")
            )
        if seconds == 0:
            await self._embed_msg(
                ctx, title=_("Setting Changed"), description=_("Track max length disabled.")
            )
        else:
            await self._embed_msg(
                ctx,
                title=_("Setting Changed"),
                description=_("Track max length set to {seconds}.").format(
                    seconds=dynamic_time(seconds)
                ),
            )
        await self.config.guild(ctx.guild).maxlength.set(seconds)