    async def seek(self, ctx: commands.Context, seconds: Union[int, str]):
        """Seek ahead or behind on a track by seconds or a to a specific time.

        Accepts seconds or a value formatted like 00:00:00 (`hh:mm:ss`) or 00:00 (`mm:ss`)."""
        dj_enabled = await self.config.guild(ctx.guild).dj_enabled()
        vote_enabled = await self.config.guild(ctx.guild).vote_enabled()
        is_alone = await self._is_alone(ctx)
        is_requester = await self.is_requester(ctx, ctx.author)
        can_skip = await self._can_instaskip(ctx, ctx.author)

        if not self._player_check(ctx):
            return await self._embed_msg(ctx, _("Nothing playing."))
        player = lavalink.get_player(ctx.guild.id)
        if (not ctx.author.voice or ctx.author.voice.channel != player.channel) and not can_skip:
            return await self._embed_msg(ctx, _("You must be in the voice channel to use seek."))

        if vote_enabled and not can_skip and not is_alone:
            return await self._embed_msg(
                ctx, _("There are other people listening - vote to skip instead.")
            )

        if dj_enabled and not (can_skip or is_requester) and not is_alone:
            return await self._embed_msg(
                ctx, _("You need the DJ role or be the track requester to use seek.")
            )

        if player.current:
            if player.current.is_stream:
                return await self._embed_msg(ctx, _("Can't seek on a stream."))
            else:
                try:
                    int(seconds)
                    abs_position = False
                except ValueError:
                    abs_position = True
                    seconds = time_convert(seconds)
                if seconds == 0:
                    return await self._embed_msg(ctx, _("Invalid input for the time to seek."))
                if not abs_position:
                    time_sec = int(seconds) * 1000
                    seek = player.position + time_sec
                    if seek <= 0:
                        await self._embed_msg(
                            ctx, _("Moved {num_seconds}s to 00:00:00").format(num_seconds=seconds)
                        )
                    else:
                        await self._embed_msg(
                            ctx,
                            _("Moved {num_seconds}s to {time}").format(
                                num_seconds=seconds, time=lavalink.utils.format_time(seek)
                            ),
                        )
                    await player.seek(seek)
                else:
                    await self._embed_msg(
                        ctx,
                        _("Moved to {time}").format(
                            time=lavalink.utils.format_time(seconds * 1000)
                        ),
                    )
                    await player.seek(seconds * 1000)
        else:
            await self._embed_msg(ctx, _("Nothing playing."))