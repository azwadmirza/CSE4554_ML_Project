    async def lavalink_query(
        self,
        ctx: commands.Context,
        player: lavalink.Player,
        query: audio_dataclasses.Query,
        forced: bool = False,
    ) -> Tuple[LoadResult, bool]:
        """A replacement for :code:`lavalink.Player.load_tracks`. This will try to get a valid
        cached entry first if not found or if in valid it will then call the lavalink API.

        Parameters
        ----------
        ctx: commands.Context
            The context this method is being called under.
        player : lavalink.Player
            The player who's requesting the query.
        query: audio_dataclasses.Query
            The Query object for the query in question.
        forced:bool
            Whether or not to skip cache and call API first..
        Returns
        -------
        Tuple[lavalink.LoadResult, bool]
            Tuple with the Load result and whether or not the API was called.
        """
        current_cache_level = CacheLevel(await self.config.cache_level())
        cache_enabled = CacheLevel.set_lavalink().is_subset(current_cache_level)
        val = None
        _raw_query = audio_dataclasses.Query.process_input(query)
        query = str(_raw_query)
        if cache_enabled and not forced and not _raw_query.is_local:
            update = True
            with contextlib.suppress(SQLError):
                (val, update) = await self.database.fetch_one("lavalink", "data", {"query": query})
            if update:
                val = None
            if val and not isinstance(val, str):
                log.debug(f"Querying Local Database for {query}")
                task = ("update", ("lavalink", {"query": query}))
                self.append_task(ctx, *task)
        if val and not forced:
            data = val
            data["query"] = query
            results = LoadResult(data)
            called_api = False
            if results.has_error:
                # If cached value has an invalid entry make a new call so that it gets updated
                return await self.lavalink_query(ctx, player, _raw_query, forced=True)
        else:
            called_api = True
            results = None
            try:
                results = await player.load_tracks(query)
            except KeyError:
                results = None
            except RuntimeError:
                raise TrackEnqueueError
            if results is None:
                results = LoadResult({"loadType": "LOAD_FAILED", "playlistInfo": {}, "tracks": []})
            if (
                cache_enabled
                and results.load_type
                and not results.has_error
                and not _raw_query.is_local
                and results.tracks
            ):
                with contextlib.suppress(SQLError):
                    time_now = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
                    task = (
                        "insert",
                        (
                            "lavalink",
                            [
                                {
                                    "query": query,
                                    "data": json.dumps(results._raw),
                                    "last_updated": time_now,
                                    "last_fetched": time_now,
                                }
                            ],
                        ),
                    )
                    self.append_task(ctx, *task)
        return results, called_api