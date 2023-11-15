    async def prev(self, ctx: commands.Context):
        """Skip to the start of the previously played track."""
        if not self._player_check(ctx):
            return await self._embed_msg(ctx, title=_("Nothing playing."))
        dj_enabled = self._dj_status_cache.setdefault(
            ctx.guild.id, await self.config.guild(ctx.guild).dj_enabled()
        )
        vote_enabled = await self.config.guild(ctx.guild).vote_enabled()
        is_alone = await self._is_alone(ctx)
        is_requester = await self.is_requester(ctx, ctx.author)
        can_skip = await self._can_instaskip(ctx, ctx.author)
        player = lavalink.get_player(ctx.guild.id)
        if (not ctx.author.voice or ctx.author.voice.channel != player.channel) and not can_skip:
            return await self._embed_msg(
                ctx,
                title=_("Unable To Skip Tracks"),
                description=_("You must be in the voice channel to skip the track."),
            )
        if vote_enabled or vote_enabled and dj_enabled:
            if not await self._can_instaskip(ctx, ctx.author) and not await self._is_alone(ctx):
                return await self._embed_msg(
                    ctx,
                    title=_("Unable To Skip Tracks"),
                    description=_("There are other people listening - vote to skip instead."),
                )
        if dj_enabled and not vote_enabled:
            if not (can_skip or is_requester) and not is_alone:
                return await self._embed_msg(
                    ctx,
                    title=_("Unable To Skip Tracks"),
                    description=_(
                        "You need the DJ role or be the track requester "
                        "to enqueue the previous song tracks."
                    ),
                )

        if player.fetch("prev_song") is None:
            return await self._embed_msg(
                ctx, title=_("Unable To Play Tracks"), description=_("No previous track.")
            )
        else:
            track = player.fetch("prev_song")
            player.add(player.fetch("prev_requester"), track)
            self.bot.dispatch("red_audio_track_enqueue", player.channel.guild, track, ctx.author)
            queue_len = len(player.queue)
            bump_song = player.queue[-1]
            player.queue.insert(0, bump_song)
            player.queue.pop(queue_len)
            await player.skip()
            description = get_track_description(player.current)
            embed = discord.Embed(title=_("Replaying Track"), description=description)
            await self._embed_msg(ctx, embed=embed)