    async def autoplay(self, ctx: commands.Context):
        """Starts auto play."""
        if not self._player_check(ctx):
            if self._connection_aborted:
                msg = _("Connection to Lavalink has failed")
                desc = EmptyEmbed
                if await ctx.bot.is_owner(ctx.author):
                    desc = _("Please check your console or logs for details.")
                return await self._embed_msg(ctx, title=msg, description=desc)
            try:
                if (
                    not ctx.author.voice.channel.permissions_for(ctx.me).connect
                    or not ctx.author.voice.channel.permissions_for(ctx.me).move_members
                    and userlimit(ctx.author.voice.channel)
                ):
                    return await self._embed_msg(
                        ctx,
                        title=_("Unable To Play Tracks"),
                        description=_("I don't have permission to connect to your channel."),
                    )
                await lavalink.connect(ctx.author.voice.channel)
                player = lavalink.get_player(ctx.guild.id)
                player.store("connect", datetime.datetime.utcnow())
            except AttributeError:
                return await self._embed_msg(
                    ctx,
                    title=_("Unable To Play Tracks"),
                    description=_("Connect to a voice channel first."),
                )
            except IndexError:
                return await self._embed_msg(
                    ctx,
                    title=_("Unable To Play Tracks"),
                    description=_("Connection to Lavalink has not yet been established."),
                )
        guild_data = await self.config.guild(ctx.guild).all()
        if guild_data["dj_enabled"]:
            if not await self._can_instaskip(ctx, ctx.author):
                return await self._embed_msg(
                    ctx,
                    title=_("Unable To Play Tracks"),
                    description=_("You need the DJ role to queue tracks."),
                )
        player = lavalink.get_player(ctx.guild.id)

        player.store("channel", ctx.channel.id)
        player.store("guild", ctx.guild.id)
        await self._eq_check(ctx, player)
        await self._data_check(ctx)
        if (
            not ctx.author.voice or ctx.author.voice.channel != player.channel
        ) and not await self._can_instaskip(ctx, ctx.author):
            return await self._embed_msg(
                ctx,
                title=_("Unable To Play Tracks"),
                description=_("You must be in the voice channel to use the autoplay command."),
            )
        if not await self._currency_check(ctx, guild_data["jukebox_price"]):
            return

        try:
            await self.music_cache.autoplay(player)
        except DatabaseError:
            notify_channel = player.fetch("channel")
            if notify_channel:
                notify_channel = self.bot.get_channel(notify_channel)
                await self._embed_msg(notify_channel, title=_("Couldn't get a valid track."))
            return

        if not guild_data["auto_play"]:
            await ctx.invoke(self._autoplay_toggle)
        if not guild_data["notify"] and (
            (player.current and not player.current.extras.get("autoplay")) or not player.current
        ):
            await self._embed_msg(ctx, title=_("Auto play started."))
        elif player.current:
            await self._embed_msg(ctx, title=_("Adding a track to queue."))