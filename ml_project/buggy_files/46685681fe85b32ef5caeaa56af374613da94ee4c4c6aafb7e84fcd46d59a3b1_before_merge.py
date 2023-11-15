    async def summon(self, ctx: commands.Context):
        """Summon the bot to a voice channel."""
        dj_enabled = await self.config.guild(ctx.guild).dj_enabled()
        if dj_enabled:
            if not await self._can_instaskip(ctx, ctx.author):
                return await self._embed_msg(ctx, _("You need the DJ role to summon the bot."))
        try:
            if (
                not ctx.author.voice.channel.permissions_for(ctx.me).connect
                or not ctx.author.voice.channel.permissions_for(ctx.me).move_members
                and userlimit(ctx.author.voice.channel)
            ):
                return await self._embed_msg(
                    ctx, _("I don't have permission to connect to your channel.")
                )
            if not self._player_check(ctx):
                await lavalink.connect(ctx.author.voice.channel)
                player = lavalink.get_player(ctx.guild.id)
                player.store("connect", datetime.datetime.utcnow())
            else:
                player = lavalink.get_player(ctx.guild.id)
                if ctx.author.voice.channel == player.channel:
                    return
                await player.move_to(ctx.author.voice.channel)
        except AttributeError:
            return await self._embed_msg(ctx, _("Connect to a voice channel first."))
        except IndexError:
            return await self._embed_msg(
                ctx, _("Connection to Lavalink has not yet been established.")
            )