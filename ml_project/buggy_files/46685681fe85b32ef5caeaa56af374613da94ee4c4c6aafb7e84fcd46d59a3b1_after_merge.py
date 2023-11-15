    async def summon(self, ctx: commands.Context):
        """Summon the bot to a voice channel."""
        dj_enabled = self._dj_status_cache.setdefault(
            ctx.guild.id, await self.config.guild(ctx.guild).dj_enabled()
        )
        vote_enabled = await self.config.guild(ctx.guild).vote_enabled()
        is_alone = await self._is_alone(ctx)
        is_requester = await self.is_requester(ctx, ctx.author)
        can_skip = await self._can_instaskip(ctx, ctx.author)
        if vote_enabled or (vote_enabled and dj_enabled):
            if not can_skip and not is_alone:
                return await self._embed_msg(
                    ctx,
                    title=_("Unable To Join Voice Channel"),
                    description=_("There are other people listening."),
                )
        if dj_enabled and not vote_enabled:
            if not (can_skip or is_requester) and not is_alone:
                return await self._embed_msg(
                    ctx,
                    title=_("Unable To Join Voice Channel"),
                    description=_("You need the DJ role to summon the bot."),
                )

        try:
            if (
                not ctx.author.voice.channel.permissions_for(ctx.me).connect
                or not ctx.author.voice.channel.permissions_for(ctx.me).move_members
                and userlimit(ctx.author.voice.channel)
            ):
                ctx.command.reset_cooldown(ctx)
                return await self._embed_msg(
                    ctx,
                    title=_("Unable To Join Voice Channel"),
                    description=_("I don't have permission to connect to your channel."),
                )
            if not self._player_check(ctx):
                await lavalink.connect(ctx.author.voice.channel)
                player = lavalink.get_player(ctx.guild.id)
                player.store("connect", datetime.datetime.utcnow())
            else:
                player = lavalink.get_player(ctx.guild.id)
                if ctx.author.voice.channel == player.channel:
                    ctx.command.reset_cooldown(ctx)
                    return
                await player.move_to(ctx.author.voice.channel)
        except AttributeError:
            ctx.command.reset_cooldown(ctx)
            return await self._embed_msg(
                ctx,
                title=_("Unable To Join Voice Channel"),
                description=_("Connect to a voice channel first."),
            )
        except IndexError:
            ctx.command.reset_cooldown(ctx)
            return await self._embed_msg(
                ctx,
                title=_("Unable To Join Voice Channel"),
                description=_("Connection to Lavalink has not yet been established."),
            )