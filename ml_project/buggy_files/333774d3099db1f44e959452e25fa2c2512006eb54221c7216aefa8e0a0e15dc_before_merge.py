    async def _localtracks_folders(self, ctx: commands.Context, search_subfolders=False):
        audio_data = audio_dataclasses.LocalPath(
            audio_dataclasses.LocalPath(None).localtrack_folder.absolute()
        )
        if not await self._localtracks_check(ctx):
            return

        return audio_data.subfolders_in_tree() if search_subfolders else audio_data.subfolders()