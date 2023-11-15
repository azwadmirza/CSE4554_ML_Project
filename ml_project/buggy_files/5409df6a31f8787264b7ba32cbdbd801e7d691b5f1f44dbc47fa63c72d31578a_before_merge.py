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
                        ctx, _("Wait until the playlist has finished loading.")
                    )
            except KeyError:
                pass
            tracks = await self._get_spotify_tracks(ctx, query)
            if not tracks:
                return await self._embed_msg(ctx, _("Nothing found."))
            for track in tracks:
                track_obj = track_creator(player, other_track=track)
                tracklist.append(track_obj)
            self._play_lock(ctx, False)
        elif query.is_search:
            result, called_api = await self.music_cache.lavalink_query(ctx, player, query)
            tracks = result.tracks
            if not tracks:
                return await self._embed_msg(ctx, _("Nothing found."))
        else:
            result, called_api = await self.music_cache.lavalink_query(ctx, player, query)
            tracks = result.tracks

        if not search and len(tracklist) == 0:
            for track in tracks:
                track_obj = track_creator(player, other_track=track)
                tracklist.append(track_obj)
        elif len(tracklist) == 0:
            track_obj = track_creator(player, other_track=tracks[0])
            tracklist.append(track_obj)
        return tracklist