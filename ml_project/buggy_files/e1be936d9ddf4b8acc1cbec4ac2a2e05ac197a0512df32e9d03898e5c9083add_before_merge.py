    async def _local_play_all(
        self, ctx: commands.Context, query: audio_dataclasses.Query, from_search=False
    ):
        if not await self._localtracks_check(ctx):
            return
        if from_search:
            query = audio_dataclasses.Query.process_input(
                query.track.to_string(), invoked_from="local folder"
            )
        await ctx.invoke(self.search, query=query)