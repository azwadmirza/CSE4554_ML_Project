    async def _queue_shuffle(self, ctx: commands.Context):
        """Shuffles the queue."""
        dj_enabled = await self.config.guild(ctx.guild).dj_enabled()
        if dj_enabled:
            if not await self._can_instaskip(ctx, ctx.author) and not await self._is_alone(ctx):
                return await self._embed_msg(ctx, _("You need the DJ role to shuffle the queue."))
        if not self._player_check(ctx):
            return await self._embed_msg(ctx, _("There's nothing in the queue."))
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
        except KeyError:
            return await self._embed_msg(ctx, _("There's nothing in the queue."))

        if not self._player_check(ctx) or not player.queue:
            return await self._embed_msg(ctx, _("There's nothing in the queue."))

        player.force_shuffle(0)
        return await self._embed_msg(ctx, _("Queue has been shuffled."))