    async def _localtracks_check(self, ctx: commands.Context):
        folder = audio_dataclasses.LocalPath(None)
        if folder.localtrack_folder.exists():
            return True
        if ctx.invoked_with != "start":
            await self._embed_msg(ctx, _("No localtracks folder."))
        return False