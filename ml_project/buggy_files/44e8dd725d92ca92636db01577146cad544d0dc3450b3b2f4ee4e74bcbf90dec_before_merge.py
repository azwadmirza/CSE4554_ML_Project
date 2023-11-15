    async def local_folder(
        self, ctx: commands.Context, play_subfolders: Optional[bool] = True, *, folder: str = None
    ):
        """Play all songs in a localtracks folder."""
        if not await self._localtracks_check(ctx):
            return

        if not folder:
            await ctx.invoke(self.local_play, play_subfolders=play_subfolders)
        else:
            folder = folder.strip()
            _dir = audio_dataclasses.LocalPath.joinpath(folder)
            if not _dir.exists():
                return await self._embed_msg(
                    ctx, _("No localtracks folder named {name}.").format(name=folder)
                )
            query = audio_dataclasses.Query.process_input(_dir, search_subfolders=play_subfolders)
            await self._local_play_all(ctx, query, from_search=False if not folder else True)