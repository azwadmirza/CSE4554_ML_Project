    async def _playlist_tracks(
        self,
        ctx: commands.Context,
        player: lavalink.player_manager.Player,
        query: audio_dataclasses.Query,
    ):
        search = query.is_search
        tracklist = []

        if query.is_spotify:
            try:
                if self.play_lock[ctx.message.guild.id]:
                    return await self._embed_msg(
                        ctx,
                        title=_("Unable To Get Tracks"),
                        description=_("Wait until the playlist has finished loading."),
                    )
            except KeyError:
                pass
            tracks = await self._get_spotify_tracks(ctx, query)

            if isinstance(tracks, discord.Message):
                return None

            if not tracks:
                embed = discord.Embed(title=_("Nothing found."))
                if (
                    query.is_local
                    and query.suffix in audio_dataclasses._PARTIALLY_SUPPORTED_MUSIC_EXT
                ):
                    embed = discord.Embed(title=_("Track is not playable."))
                    embed.description = _(
                        "**{suffix}** is not a fully supported format and some "
                        "tracks may not play."
                    ).format(suffix=query.suffix)
                return await self._embed_msg(ctx, embed=embed)
            for track in tracks:
                track_obj = track_creator(player, other_track=track)
                tracklist.append(track_obj)
            self._play_lock(ctx, False)
        elif query.is_search:
            try:
                result, called_api = await self.music_cache.lavalink_query(ctx, player, query)
            except TrackEnqueueError:
                self._play_lock(ctx, False)
                return await self._embed_msg(
                    ctx,
                    title=_("Unable to Get Track"),
                    description=_(
                        "I'm unable get a track from Lavalink at the moment, try again in a few "
                        "minutes."
                    ),
                )

            tracks = result.tracks
            if not tracks:
                embed = discord.Embed(title=_("Nothing found."))
                if (
                    query.is_local
                    and query.suffix in audio_dataclasses._PARTIALLY_SUPPORTED_MUSIC_EXT
                ):
                    embed = discord.Embed(title=_("Track is not playable."))
                    embed.description = _(
                        "**{suffix}** is not a fully supported format and some "
                        "tracks may not play."
                    ).format(suffix=query.suffix)
                return await self._embed_msg(ctx, embed=embed)
        else:
            try:
                result, called_api = await self.music_cache.lavalink_query(ctx, player, query)
            except TrackEnqueueError:
                self._play_lock(ctx, False)
                return await self._embed_msg(
                    ctx,
                    title=_("Unable to Get Track"),
                    description=_(
                        "I'm unable get a track from Lavalink at the moment, try again in a few "
                        "minutes."
                    ),
                )

            tracks = result.tracks

        if not search and len(tracklist) == 0:
            for track in tracks:
                track_obj = track_creator(player, other_track=track)
                tracklist.append(track_obj)
        elif len(tracklist) == 0:
            track_obj = track_creator(player, other_track=tracks[0])
            tracklist.append(track_obj)
        return tracklist