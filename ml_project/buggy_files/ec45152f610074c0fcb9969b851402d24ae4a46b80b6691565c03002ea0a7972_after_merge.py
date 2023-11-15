    async def _folder_list(self, ctx, folder):
        if not await self._localtracks_check(ctx):
            return
        if not os.path.isdir(os.getcwd() + "/localtracks/{}/".format(folder)):
            return
        allowed_files = (".mp3", ".flac", ".ogg")
        folder_list = sorted(
            (
                os.getcwd() + "/localtracks/{}/{}".format(folder, f)
                for f in os.listdir(os.getcwd() + "/localtracks/{}/".format(folder))
                if (f.lower().endswith(allowed_files))
                and (os.path.isfile(os.getcwd() + "/localtracks/{}/{}".format(folder, f)))
            ),
            key=lambda s: s.casefold(),
        )
        track_listing = []
        if ctx.invoked_with == "search":
            local_path = await self.config.localpath()
            for localtrack_location in folder_list:
                track_listing.append(
                    localtrack_location.replace("{}/localtracks/".format(local_path), "")
                )
        else:
            for localtrack_location in folder_list:
                localtrack_location = "localtrack:{}".format(localtrack_location)
                track_listing.append(localtrack_location)
        return track_listing