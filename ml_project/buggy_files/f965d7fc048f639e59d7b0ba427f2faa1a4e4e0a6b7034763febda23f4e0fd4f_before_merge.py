    async def _get_spotify_tracks(self, ctx: commands.Context, query: audio_dataclasses.Query):
        if ctx.invoked_with in ["play", "genre"]:
            enqueue_tracks = True
        else:
            enqueue_tracks = False
        player = lavalink.get_player(ctx.guild.id)
        api_data = await self._check_api_tokens()

        if (
            not api_data["spotify_client_id"]
            or not api_data["spotify_client_secret"]
            or not api_data["youtube_api"]
        ):
            return await self._embed_msg(
                ctx,
                _(
                    "The owner needs to set the Spotify client ID, Spotify client secret, "
                    "and YouTube API key before Spotify URLs or codes can be used. "
                    "\nSee `{prefix}audioset youtubeapi` and `{prefix}audioset spotifyapi` "
                    "for instructions."
                ).format(prefix=ctx.prefix),
            )
        try:
            if self.play_lock[ctx.message.guild.id]:
                return await self._embed_msg(
                    ctx, _("Wait until the playlist has finished loading.")
                )
        except KeyError:
            pass

        if query.single_track:
            try:
                res = await self.music_cache.spotify_query(
                    ctx, "track", query.id, skip_youtube=True, notifier=None
                )
                if not res:
                    return await self._embed_msg(ctx, _("Nothing found."))
            except SpotifyFetchError as error:
                self._play_lock(ctx, False)
                return await self._embed_msg(ctx, _(error.message).format(prefix=ctx.prefix))
            self._play_lock(ctx, False)
            try:
                if enqueue_tracks:
                    new_query = audio_dataclasses.Query.process_input(res[0])
                    new_query.start_time = query.start_time
                    return await self._enqueue_tracks(ctx, new_query)
                else:
                    result, called_api = await self.music_cache.lavalink_query(
                        ctx, player, audio_dataclasses.Query.process_input(res[0])
                    )
                    tracks = result.tracks
                    if not tracks:
                        return await self._embed_msg(ctx, _("Nothing found."))
                    single_track = tracks[0]
                    single_track.start_timestamp = query.start_time * 1000
                    single_track = [single_track]

                    return single_track

            except KeyError:
                self._play_lock(ctx, False)
                return await self._embed_msg(
                    ctx,
                    _(
                        "The Spotify API key or client secret has not been set properly. "
                        "\nUse `{prefix}audioset spotifyapi` for instructions."
                    ).format(prefix=ctx.prefix),
                )
        elif query.is_album or query.is_playlist:
            self._play_lock(ctx, True)
            track_list = await self._spotify_playlist(
                ctx, "album" if query.is_album else "playlist", query, enqueue_tracks
            )
            self._play_lock(ctx, False)
            return track_list
        else:
            return await self._embed_msg(
                ctx, _("This doesn't seem to be a supported Spotify URL or code.")
            )