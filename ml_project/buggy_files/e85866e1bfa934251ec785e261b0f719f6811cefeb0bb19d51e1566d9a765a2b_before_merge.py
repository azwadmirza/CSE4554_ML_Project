async def delete_playlist(
    scope: str,
    playlist_id: Union[str, int],
    guild: discord.Guild,
    author: Union[discord.abc.User, int] = None,
) -> None:
    """
        Deletes the specified playlist.

        Parameters
        ----------
        scope: str
            The custom config scope. One of 'GLOBALPLAYLIST', 'GUILDPLAYLIST' or 'USERPLAYLIST'.
        playlist_id: Union[str, int]
            The ID of the playlist.
        guild: discord.Guild
            The guild to get the playlist from if scope is GUILDPLAYLIST.
        author: int
            The ID of the user to get the playlist from if scope is USERPLAYLIST.

         Raises
        ------
        `InvalidPlaylistScope`
            Passing a scope that is not supported.
        `MissingGuild`
            Trying to access the Guild scope without a guild.
        `MissingAuthor`
            Trying to access the User scope without an user id.
        """
    await _config.custom(*_prepare_config_scope(scope, author, guild), str(playlist_id)).clear()