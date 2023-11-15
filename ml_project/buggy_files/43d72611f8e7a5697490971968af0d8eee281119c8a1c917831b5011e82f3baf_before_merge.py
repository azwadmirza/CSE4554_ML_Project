    async def _skip_action(self, ctx: commands.Context, skip_to_track: int = None):
        player = lavalink.get_player(ctx.guild.id)
        autoplay = await self.config.guild(player.channel.guild).auto_play() or self.owns_autoplay
        if not player.current or (not player.queue and not autoplay):
            try:
                pos, dur = player.position, player.current.length
            except AttributeError:
                return await self._embed_msg(ctx, _("There's nothing in the queue."))
            time_remain = lavalink.utils.format_time(dur - pos)
            if player.current.is_stream:
                embed = discord.Embed(
                    colour=await ctx.embed_colour(), title=_("There's nothing in the queue.")
                )
                embed.set_footer(
                    text=_("Currently livestreaming {track}").format(track=player.current.title)
                )
            else:
                embed = discord.Embed(
                    colour=await ctx.embed_colour(), title=_("There's nothing in the queue.")
                )
                embed.set_footer(
                    text=_("{time} left on {track}").format(
                        time=time_remain, track=player.current.title
                    )
                )
            return await ctx.send(embed=embed)
        elif autoplay and not player.queue:
            embed = discord.Embed(
                colour=await ctx.embed_colour(),
                title=_("Track Skipped"),
                description=await get_description(player.current),
            )
            await ctx.send(embed=embed)
            return await player.skip()

        queue_to_append = []
        if skip_to_track is not None and skip_to_track != 1:
            if skip_to_track < 1:
                return await self._embed_msg(
                    ctx, _("Track number must be equal to or greater than 1.")
                )
            elif skip_to_track > len(player.queue):
                return await self._embed_msg(
                    ctx,
                    _(
                        "There are only {queuelen} songs currently queued.".format(
                            queuelen=len(player.queue)
                        )
                    ),
                )
            embed = discord.Embed(
                colour=await ctx.embed_colour(),
                title=_("{skip_to_track} Tracks Skipped".format(skip_to_track=skip_to_track)),
            )
            await ctx.send(embed=embed)
            if player.repeat:
                queue_to_append = player.queue[0 : min(skip_to_track - 1, len(player.queue) - 1)]
            player.queue = player.queue[
                min(skip_to_track - 1, len(player.queue) - 1) : len(player.queue)
            ]
        else:
            embed = discord.Embed(
                colour=await ctx.embed_colour(),
                title=_("Track Skipped"),
                description=await get_description(player.current),
            )
            await ctx.send(embed=embed)
        self.bot.dispatch("red_audio_skip_track", player.channel.guild, player.current, ctx.author)
        await player.play()
        player.queue += queue_to_append