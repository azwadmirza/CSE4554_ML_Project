    async def _playlist_create(
        self, ctx: commands.Context, playlist_name: str, *, scope_data: ScopeParser = None
    ):
        """Create an empty playlist.

        **Usage**:
        ​ ​ ​ ​ [p]playlist create playlist_name args

        **Args**:
        ​ ​ ​ ​ The following are all optional:
        ​ ​ ​ ​ ​ ​ ​ ​ --scope <scope>
        ​ ​ ​ ​ ​ ​ ​ ​ --author [user]
        ​ ​ ​ ​ ​ ​ ​ ​ --guild [guild] **Only the bot owner can use this**

        **Scope** is one of the following:
        ​ ​ ​ ​ Global
        ​ ​ ​ ​ Guild
        ​ ​ ​ ​ User

        **Author** can be one of the following:
        ​ ​ ​ ​ User ID
        ​ ​ ​ ​ User Mention
        ​ ​ ​ ​ User Name#123

        **Guild** can be one of the following:
        ​ ​ ​ ​ Guild ID
        ​ ​ ​ ​ Exact guild name

        Example use:
        ​ ​ ​ ​ [p]playlist create MyGuildPlaylist
        ​ ​ ​ ​ [p]playlist create MyGlobalPlaylist --scope Global
        ​ ​ ​ ​ [p]playlist create MyPersonalPlaylist --scope User
        """
        if scope_data is None:
            scope_data = [PlaylistScope.GUILD.value, ctx.author, ctx.guild, False]
        scope, author, guild, specified_user = scope_data

        temp_playlist = FakePlaylist(author.id, scope)
        scope_name = humanize_scope(
            scope, ctx=guild if scope == PlaylistScope.GUILD.value else author
        )
        if not await self.can_manage_playlist(scope, temp_playlist, ctx, author, guild):
            return
        playlist_name = playlist_name.split(" ")[0].strip('"')[:32]
        if playlist_name.isnumeric():
            return await self._embed_msg(
                ctx,
                title=_("Invalid Playlist Name"),
                description=_(
                    "Playlist names must be a single word (up to 32 "
                    "characters) and not numbers only."
                ),
            )
        playlist = await create_playlist(ctx, scope, playlist_name, None, None, author, guild)
        return await self._embed_msg(
            ctx,
            title=_("Playlist Created"),
            description=_("Empty playlist {name} (`{id}`) [**{scope}**] created.").format(
                name=playlist.name, id=playlist.id, scope=scope_name
            ),
        )