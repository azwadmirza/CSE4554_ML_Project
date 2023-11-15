    async def _folder_tracks(
        self, ctx, player: lavalink.player_manager.Player, query: audio_dataclasses.Query
    ):
        if not await self._localtracks_check(ctx):
            return

        audio_data = audio_dataclasses.LocalPath(None)
        try:
            query.track.path.relative_to(audio_data.to_string())
        except ValueError:
            return
        local_tracks = []
        for local_file in await self._all_folder_tracks(ctx, query):
            trackdata, called_api = await self.music_cache.lavalink_query(ctx, player, local_file)
            with contextlib.suppress(IndexError):
                local_tracks.append(trackdata.tracks[0])
        return local_tracks