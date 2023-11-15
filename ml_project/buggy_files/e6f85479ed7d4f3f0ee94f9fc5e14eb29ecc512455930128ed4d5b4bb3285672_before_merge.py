    async def prev(self, ctx: commands.Context):
        """Skip to the start of the previously played track."""
        if not self._player_check(ctx):
            return await self._embed_msg(ctx, _("Nothing playing."))
        dj_enabled = await self.config.guild(ctx.guild).dj_enabled()
        player = lavalink.get_player(ctx.guild.id)
        if dj_enabled:
            if not await self._can_instaskip(ctx, ctx.author) and not await self._is_alone(ctx):
                return await self._embed_msg(ctx, _("You need the DJ role to skip tracks."))
        if (
            not ctx.author.voice or ctx.author.voice.channel != player.channel
        ) and not await self._can_instaskip(ctx, ctx.author):
            return await self._embed_msg(
                ctx, _("You must be in the voice channel to skip the music.")
            )
        if player.fetch("prev_song") is None:
            return await self._embed_msg(ctx, _("No previous track."))
        else:
            track = player.fetch("prev_song")
            player.add(player.fetch("prev_requester"), track)
            self.bot.dispatch("red_audio_track_enqueue", player.channel.guild, track, ctx.author)
            queue_len = len(player.queue)
            bump_song = player.queue[-1]
            player.queue.insert(0, bump_song)
            player.queue.pop(queue_len)
            await player.skip()
            query = audio_dataclasses.Query.process_input(player.current.uri)
            if query.is_local:

                if player.current.title == "Unknown title":
                    description = "{}".format(query.track.to_string_hidden())
                else:
                    song = bold("{} - {}").format(player.current.author, player.current.title)
                    description = "{}\n{}".format(song, query.track.to_string_hidden())
            else:
                description = f"**[{player.current.title}]({player.current.uri})**"
            embed = discord.Embed(
                colour=await ctx.embed_colour(),
                title=_("Replaying Track"),
                description=description,
            )
            await ctx.send(embed=embed)