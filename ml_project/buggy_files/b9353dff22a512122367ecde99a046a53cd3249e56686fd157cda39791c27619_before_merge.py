async def reset_playlist(
    scope: str,
    guild: Union[discord.Guild, int] = None,
    author: Union[discord.abc.User, int] = None,
) -> None:
    """
    Wipes all playlists for the specified scope.

    Parameters
    ----------
    scope: str
        The custom config scope. One of 'GLOBALPLAYLIST', 'GUILDPLAYLIST' or 'USERPLAYLIST'.
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
    await _config.custom(*_prepare_config_scope(scope, author, guild)).clear()