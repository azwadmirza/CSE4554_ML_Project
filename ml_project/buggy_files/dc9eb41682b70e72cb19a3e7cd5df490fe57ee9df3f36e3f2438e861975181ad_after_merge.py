    async def _all_folder_tracks(
        self, ctx: commands.Context, query: audio_dataclasses.Query
    ) -> Optional[List[audio_dataclasses.Query]]:
        if not await self._localtracks_check(ctx):
            return

        return (
            query.track.tracks_in_tree()
            if query.search_subfolders
            else query.track.tracks_in_folder()
        )