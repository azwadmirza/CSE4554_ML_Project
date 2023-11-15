    async def youtube_query(self, ctx: commands.Context, track_info: str) -> str:
        current_cache_level = (
            CacheLevel(await self.config.cache_level()) if HAS_SQL else CacheLevel.none()
        )
        cache_enabled = CacheLevel.set_youtube().is_subset(current_cache_level)
        val = None
        if cache_enabled:
            update = True
            with contextlib.suppress(SQLError):
                val, update = await self.fetch_one("youtube", "youtube_url", {"track": track_info})
            if update:
                val = None
        if val is None:
            youtube_url = await self._youtube_first_time_query(
                ctx, track_info, current_cache_level=current_cache_level
            )
        else:
            if cache_enabled:
                task = ("update", ("youtube", {"track": track_info}))
                self.append_task(ctx, *task)
            youtube_url = val
        return youtube_url