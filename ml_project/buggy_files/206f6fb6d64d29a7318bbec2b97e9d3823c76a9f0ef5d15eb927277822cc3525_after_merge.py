async def get_all_playlist(
    scope: str,
    bot: Red,
    guild: Union[discord.Guild, int] = None,
    author: Union[discord.abc.User, int] = None,
    specified_user: bool = False,
) -> List[Playlist]:
    """
    Gets all playlist for the specified scope.
    Parameters
    ----------
    scope: str
        The custom config scope. One of 'GLOBALPLAYLIST', 'GUILDPLAYLIST' or 'USERPLAYLIST'.
    guild: discord.Guild
        The guild to get the playlist from if scope is GUILDPLAYLIST.
    author: int
        The ID of the user to get the playlist from if scope is USERPLAYLIST.
    bot: Red
        The bot's instance
    specified_user:bool
        Whether or not user ID was passed as an argparse.
    Returns
    -------
    list
        A list of all playlists for the specified scope
     Raises
    ------
    `InvalidPlaylistScope`
        Passing a scope that is not supported.
    `MissingGuild`
        Trying to access the Guild scope without a guild.
    `MissingAuthor`
        Trying to access the User scope without an user id.
    """
    scope_standard, scope_id = _prepare_config_scope(scope, author, guild)

    if specified_user:
        user_id = getattr(author, "id", author)
        playlists = await database.fetch_all(scope_standard, scope_id, author_id=user_id)
    else:
        playlists = await database.fetch_all(scope_standard, scope_id)
    return [
        await Playlist.from_json(
            bot, scope, playlist.playlist_id, playlist, guild=guild, author=author
        )
        for playlist in playlists
    ]