    async def play(self, ctx: commands.Context, *, query: str):
        """Play a URL or search for a track."""
        guild_data = await self.config.guild(ctx.guild).all()
        restrict = await self.config.restrict()
        if restrict and match_url(query):
            valid_url = url_check(query)
            if not valid_url:
                return await self._embed_msg(ctx, _("That URL is not allowed."))
        if not self._player_check(ctx):
            if self._connection_aborted:
                msg = _("Connection to Lavalink has failed.")
                if await ctx.bot.is_owner(ctx.author):
                    msg += " " + _("Please check your console or logs for details.")
                return await self._embed_msg(ctx, msg)
            try:
                if (
                    not ctx.author.voice.channel.permissions_for(ctx.me).connect
                    or not ctx.author.voice.channel.permissions_for(ctx.me).move_members
                    and userlimit(ctx.author.voice.channel)
                ):
                    return await self._embed_msg(
                        ctx, _("I don't have permission to connect to your channel.")
                    )
                await lavalink.connect(ctx.author.voice.channel)
                player = lavalink.get_player(ctx.guild.id)
                player.store("connect", datetime.datetime.utcnow())
            except AttributeError:
                return await self._embed_msg(ctx, _("Connect to a voice channel first."))
            except IndexError:
                return await self._embed_msg(
                    ctx, _("Connection to Lavalink has not yet been established.")
                )
        if guild_data["dj_enabled"]:
            if not await self._can_instaskip(ctx, ctx.author):
                return await self._embed_msg(ctx, _("You need the DJ role to queue tracks."))
        player = lavalink.get_player(ctx.guild.id)

        player.store("channel", ctx.channel.id)
        player.store("guild", ctx.guild.id)
        await self._eq_check(ctx, player)
        await self._data_check(ctx)
        if (
            not ctx.author.voice or ctx.author.voice.channel != player.channel
        ) and not await self._can_instaskip(ctx, ctx.author):
            return await self._embed_msg(
                ctx, _("You must be in the voice channel to use the play command.")
            )
        if not await self._currency_check(ctx, guild_data["jukebox_price"]):
            return
        query = audio_dataclasses.Query.process_input(query)
        if not query.valid:
            return await self._embed_msg(ctx, _("No tracks to play."))
        if query.is_spotify:
            return await self._get_spotify_tracks(ctx, query)
        await self._enqueue_tracks(ctx, query)