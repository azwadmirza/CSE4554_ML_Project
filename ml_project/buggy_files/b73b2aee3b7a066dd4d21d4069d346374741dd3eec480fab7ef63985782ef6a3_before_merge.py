    async def queue(self, ctx: commands.Context, *, page: int = 1):
        """List the songs in the queue."""

        async def _queue_menu(
            ctx: commands.Context,
            pages: list,
            controls: dict,
            message: discord.Message,
            page: int,
            timeout: float,
            emoji: str,
        ):
            if message:
                await ctx.send_help(self.queue)
                with contextlib.suppress(discord.HTTPException):
                    await message.delete()
                return None

        queue_controls = {"⬅": prev_page, "❌": close_menu, "➡": next_page, "ℹ": _queue_menu}

        if not self._player_check(ctx):
            return await self._embed_msg(ctx, _("There's nothing in the queue."))
        player = lavalink.get_player(ctx.guild.id)
        if not player.queue:
            if player.current:
                arrow = await draw_time(ctx)
                pos = lavalink.utils.format_time(player.position)
                if player.current.is_stream:
                    dur = "LIVE"
                else:
                    dur = lavalink.utils.format_time(player.current.length)

                query = audio_dataclasses.Query.process_input(player.current)

                if query.is_local:
                    if player.current.title != "Unknown title":
                        song = "**{track.author} - {track.title}**\n{uri}\n"
                    else:
                        song = "{uri}\n"
                else:
                    song = "**[{track.title}]({track.uri})**\n"
                song += _("Requested by: **{track.requester}**")
                song += "\n\n{arrow}`{pos}`/`{dur}`"
                song = song.format(
                    track=player.current,
                    uri=audio_dataclasses.LocalPath(player.current.uri).to_string_hidden()
                    if audio_dataclasses.Query.process_input(player.current.uri).is_local
                    else player.current.uri,
                    arrow=arrow,
                    pos=pos,
                    dur=dur,
                )

                embed = discord.Embed(
                    colour=await ctx.embed_colour(), title=_("Now Playing"), description=song
                )
                if await self.config.guild(ctx.guild).thumbnail() and player.current:
                    if player.current.thumbnail:
                        embed.set_thumbnail(url=player.current.thumbnail)

                shuffle = await self.config.guild(ctx.guild).shuffle()
                repeat = await self.config.guild(ctx.guild).repeat()
                autoplay = await self.config.guild(ctx.guild).auto_play() or self.owns_autoplay
                text = ""
                text += (
                    _("Auto-Play")
                    + ": "
                    + ("\N{WHITE HEAVY CHECK MARK}" if autoplay else "\N{CROSS MARK}")
                )
                text += (
                    (" | " if text else "")
                    + _("Shuffle")
                    + ": "
                    + ("\N{WHITE HEAVY CHECK MARK}" if shuffle else "\N{CROSS MARK}")
                )
                text += (
                    (" | " if text else "")
                    + _("Repeat")
                    + ": "
                    + ("\N{WHITE HEAVY CHECK MARK}" if repeat else "\N{CROSS MARK}")
                )
                embed.set_footer(text=text)

                return await ctx.send(embed=embed)
            return await self._embed_msg(ctx, _("There's nothing in the queue."))

        async with ctx.typing():
            len_queue_pages = math.ceil(len(player.queue) / 10)
            queue_page_list = []
            for page_num in range(1, len_queue_pages + 1):
                embed = await self._build_queue_page(ctx, player, page_num)
                queue_page_list.append(embed)
            if page > len_queue_pages:
                page = len_queue_pages
        return await menu(ctx, queue_page_list, queue_controls, page=(page - 1))