    async def _playlist_check(self, ctx: commands.Context):
        if not self._player_check(ctx):
            if self._connection_aborted:
                msg = _("Connection to Lavalink has failed")
                desc = EmptyEmbed
                if await ctx.bot.is_owner(ctx.author):
                    desc = _("Please check your console or logs for details.")
                await self._embed_msg(ctx, title=msg, description=desc)
                return False
            try:
                if (
                    not ctx.author.voice.channel.permissions_for(ctx.me).connect
                    or not ctx.author.voice.channel.permissions_for(ctx.me).move_members
                    and userlimit(ctx.author.voice.channel)
                ):
                    await self._embed_msg(
                        ctx,
                        title=_("Unable To Get Playlists"),
                        description=_("I don't have permission to connect to your channel."),
                    )
                    return False
                await lavalink.connect(ctx.author.voice.channel)
                player = lavalink.get_player(ctx.guild.id)
                player.store("connect", datetime.datetime.utcnow())
            except IndexError:
                await self._embed_msg(
                    ctx,
                    title=_("Unable To Get Playlists"),
                    description=_("Connection to Lavalink has not yet been established."),
                )
                return False
            except AttributeError:
                await self._embed_msg(
                    ctx,
                    title=_("Unable To Get Playlists"),
                    description=_("Connect to a voice channel first."),
                )
                return False

        player = lavalink.get_player(ctx.guild.id)
        player.store("channel", ctx.channel.id)
        player.store("guild", ctx.guild.id)
        if (
            not ctx.author.voice or ctx.author.voice.channel != player.channel
        ) and not await self._can_instaskip(ctx, ctx.author):
            await self._embed_msg(
                ctx,
                title=_("Unable To Get Playlists"),
                description=_("You must be in the voice channel to use the playlist command."),
            )
            return False
        await self._eq_check(ctx, player)
        await self._data_check(ctx)
        return True