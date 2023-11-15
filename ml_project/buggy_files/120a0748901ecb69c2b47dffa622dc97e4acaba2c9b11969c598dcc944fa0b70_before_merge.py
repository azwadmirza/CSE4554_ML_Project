    async def _folder_tracks(self, ctx, player, folder):
        if not await self._localtracks_check(ctx):
            return
        local_tracks = []
        for local_file in await self._all_folder_tracks(ctx, folder):
            track = await player.get_tracks("localtracks/{}/{}".format(folder, local_file))
            try:
                local_tracks.append(track[0])
            except IndexError:
                pass
        return local_tracks