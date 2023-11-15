    async def get_embed_color(self, location: discord.abc.Messageable) -> discord.Color:
        """
        Get the embed color for a location.

        Parameters
        ----------
        location : `discord.abc.Messageable`

        Returns
        -------
        discord.Color
        """

        guild = getattr(location, "guild", None)

        if (
            guild
            and await self._config.guild(guild).use_bot_color()
            and not isinstance(location, discord.Member)
        ):
            return guild.me.color

        return self._color