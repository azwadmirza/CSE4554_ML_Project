    async def _spotify_playlist(
        self,
        ctx: commands.Context,
        stype: str,
        query: audio_dataclasses.Query,
        enqueue: bool = False,
    ):

        player = lavalink.get_player(ctx.guild.id)
        try:
            embed1 = discord.Embed(
                colour=await ctx.embed_colour(), title=_("Please wait, finding tracks...")
            )
            playlist_msg = await ctx.send(embed=embed1)
            notifier = Notifier(
                ctx,
                playlist_msg,
                {
                    "spotify": _("Getting track {num}/{total}..."),
                    "youtube": _("Matching track {num}/{total}..."),
                    "lavalink": _("Loading track {num}/{total}..."),
                    "lavalink_time": _("Approximate time remaining: {seconds}"),
                },
            )
            track_list = await self.music_cache.spotify_enqueue(
                ctx,
                stype,
                query.id,
                enqueue=enqueue,
                player=player,
                lock=self._play_lock,
                notifier=notifier,
            )
        except SpotifyFetchError as error:
            self._play_lock(ctx, False)
            return await self._embed_msg(ctx, _(error.message).format(prefix=ctx.prefix))
        except (RuntimeError, aiohttp.ServerDisconnectedError):
            self._play_lock(ctx, False)
            error_embed = discord.Embed(
                colour=await ctx.embed_colour(),
                title=_("The connection was reset while loading the playlist."),
            )
            await ctx.send(embed=error_embed)
            return None
        except Exception as e:
            self._play_lock(ctx, False)
            raise e
        self._play_lock(ctx, False)
        return track_list