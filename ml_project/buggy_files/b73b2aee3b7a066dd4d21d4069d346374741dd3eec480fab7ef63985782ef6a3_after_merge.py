    async def queue(self, ctx: commands.Context, *, page: int = 1):
        """List the songs in the queue."""

        async def _queue_menu(
            ctx: commands.Context,
            pages: list,
            controls: MutableMapping,
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

        queue_controls = {
            "\N{LEFTWARDS BLACK ARROW}": prev_page,
            "\N{CROSS MARK}": close_menu,
            "\N{BLACK RIGHTWARDS ARROW}": next_page,
            "\N{INFORMATION SOURCE}": _queue_menu,
        }

        if not self._player_check(ctx):
            return await self._embed_msg(ctx, title=_("There's nothing in the queue."))
        player = lavalink.get_player(ctx.guild.id)
        if not player.queue:
            if player.current:
                arrow = await draw_time(ctx)
                pos = lavalink.utils.format_time(player.position)
                if player.current.is_stream:
                    dur = "LIVE"
                else:
                    dur = lavalink.utils.format_time(player.current.length)
                song = get_track_description(player.current)
                song += _("\n Requested by: **{track.requester}**")
                song += "\n\n{arrow}`{pos}`/`{dur}`"
                song = song.format(track=player.current, arrow=arrow, pos=pos, dur=dur)
                embed = discord.Embed(title=_("Now Playing"), description=song)
                if await self.config.guild(ctx.guild).thumbnail() and player.current:
                    if player.current.thumbnail:
                        embed.set_thumbnail(url=player.current.thumbnail)

                shuffle = await self.config.guild(ctx.guild).shuffle()
                repeat = await self.config.guild(ctx.guild).repeat()
                autoplay = await self.config.guild(ctx.guild).auto_play()
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
                message = await self._embed_msg(ctx, embed=embed)
                dj_enabled = self._dj_status_cache.setdefault(
                    ctx.guild.id, await self.config.guild(ctx.guild).dj_enabled()
                )
                vote_enabled = await self.config.guild(ctx.guild).vote_enabled()
                if dj_enabled or vote_enabled:
                    if not await self._can_instaskip(ctx, ctx.author) and not await self._is_alone(
                        ctx
                    ):
                        return

                expected = ("⏹", "⏯")
                emoji = {"stop": "⏹", "pause": "⏯"}
                if player.current:
                    task = start_adding_reactions(message, expected[:4], ctx.bot.loop)
                else:
                    task = None

                try:
                    (r, u) = await self.bot.wait_for(
                        "reaction_add",
                        check=ReactionPredicate.with_emojis(expected, message, ctx.author),
                        timeout=30.0,
                    )
                except asyncio.TimeoutError:
                    return await self._clear_react(message, emoji)
                else:
                    if task is not None:
                        task.cancel()
                reacts = {v: k for k, v in emoji.items()}
                react = reacts[r.emoji]
                if react == "stop":
                    await self._clear_react(message, emoji)
                    return await ctx.invoke(self.stop)
                elif react == "pause":
                    await self._clear_react(message, emoji)
                    return await ctx.invoke(self.pause)
                return
            return await self._embed_msg(ctx, title=_("There's nothing in the queue."))

        async with ctx.typing():
            len_queue_pages = math.ceil(len(player.queue) / 10)
            queue_page_list = []
            for page_num in range(1, len_queue_pages + 1):
                embed = await self._build_queue_page(ctx, player, page_num)
                queue_page_list.append(embed)
            if page > len_queue_pages:
                page = len_queue_pages
        return await menu(ctx, queue_page_list, queue_controls, page=(page - 1))