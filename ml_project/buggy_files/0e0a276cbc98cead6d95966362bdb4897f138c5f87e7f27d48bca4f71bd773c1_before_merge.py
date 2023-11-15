    def to_json(self) -> dict:
        """Transform the object to a dict.
        Returns
        -------
        dict
            The playlist in the form of a dict.
        """
        data = dict(
            id=self.id,
            author=self.author,
            guild=self.guild_id,
            name=self.name,
            playlist_url=self.url,
            tracks=self.tracks,
        )

        return data