    def process_input(cls, query: Union[LocalPath, lavalink.Track, "Query", str], **kwargs):
        """
        A replacement for :code:`lavalink.Player.load_tracks`.
        This will try to get a valid cached entry first if not found or if in valid
        it will then call the lavalink API.

        Parameters
        ----------
        query : Union[Query, LocalPath, lavalink.Track, str]
            The query string or LocalPath object.
        Returns
        -------
        Query
            Returns a parsed Query object.
        """
        if not query:
            query = "InvalidQueryPlaceHolderName"
        possible_values = dict()

        if isinstance(query, str):
            query = query.strip("<>")

        elif isinstance(query, Query):
            for key, val in kwargs.items():
                setattr(query, key, val)
            return query
        elif isinstance(query, lavalink.Track):
            possible_values["stream"] = query.is_stream
            query = query.uri

        possible_values.update(dict(**kwargs))
        possible_values.update(cls._parse(query, **kwargs))
        return cls(query, **possible_values)