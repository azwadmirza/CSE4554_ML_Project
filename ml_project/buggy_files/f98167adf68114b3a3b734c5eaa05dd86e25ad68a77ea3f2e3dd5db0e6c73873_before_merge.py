    async def _folder_list(self, ctx: commands.Context, query: audio_dataclasses.Query):
        if not await self._localtracks_check(ctx):
            return
        query = audio_dataclasses.Query.process_input(query)
        if not query.track.exists():
            return
        return (
            query.track.tracks_in_tree()
            if query.search_subfolders
            else query.track.tracks_in_folder()
        )