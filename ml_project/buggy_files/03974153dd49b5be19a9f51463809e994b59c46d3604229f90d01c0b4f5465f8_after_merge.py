    async def local_search(
        self, ctx: commands.Context, search_subfolders: Optional[bool] = True, *, search_words
    ):
        """Search for songs across all localtracks folders."""
        if not await self._localtracks_check(ctx):
            return
        all_tracks = await self._folder_list(
            ctx,
            (
                audio_dataclasses.Query.process_input(
                    audio_dataclasses.LocalPath(
                        await self.config.localpath()
                    ).localtrack_folder.absolute(),
                    search_subfolders=search_subfolders,
                )
            ),
        )
        if not all_tracks:
            return await self._embed_msg(ctx, title=_("No album folders found."))
        async with ctx.typing():
            search_list = await self._build_local_search_list(all_tracks, search_words)
        if not search_list:
            return await self._embed_msg(ctx, title=_("No matches."))
        return await ctx.invoke(self.search, query=search_list)