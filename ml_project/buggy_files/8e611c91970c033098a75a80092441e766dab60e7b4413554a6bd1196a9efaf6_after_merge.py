    async def _playlist_rename(
        self,
        ctx: commands.Context,
        playlist_matches: PlaylistConverter,
        new_name: str,
        *,
        scope_data: ScopeParser = None,
    ):
        """Rename an existing playlist.

        **Usage**:
        ​ ​ ​ ​ [p]playlist rename playlist_name_OR_id new_name args

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
        ​ ​ ​ ​ [p]playlist rename MyGuildPlaylist RenamedGuildPlaylist
        ​ ​ ​ ​ [p]playlist rename MyGlobalPlaylist RenamedGlobalPlaylist --scope Global
        ​ ​ ​ ​ [p]playlist rename MyPersonalPlaylist RenamedPersonalPlaylist --scope User
        """
        if scope_data is None:
            scope_data = [PlaylistScope.GUILD.value, ctx.author, ctx.guild, False]
        scope, author, guild, specified_user = scope_data

        new_name = new_name.split(" ")[0].strip('"')[:32]
        if new_name.isnumeric():
            return await self._embed_msg(
                ctx,
                title=_("Invalid Playlist Name"),
                description=_(
                    "Playlist names must be a single word (up to 32 "
                    "characters) and not numbers only."
                ),
            )

        try:
            playlist_id, playlist_arg = await self._get_correct_playlist_id(
                ctx, playlist_matches, scope, author, guild, specified_user
            )
        except TooManyMatches as e:
            return await self._embed_msg(ctx, title=str(e))
        if playlist_id is None:
            return await self._embed_msg(
                ctx,
                title=_("Playlist Not Found"),
                description=_("Could not match '{arg}' to a playlist.").format(arg=playlist_arg),
            )

        try:
            playlist = await get_playlist(playlist_id, scope, self.bot, guild, author)
        except RuntimeError:
            return await self._embed_msg(
                ctx,
                title=_("Playlist Not Found"),
                description=_("Playlist does not exist in {scope} scope.").format(
                    scope=humanize_scope(scope, the=True)
                ),
            )
        except MissingGuild:
            return await self._embed_msg(
                ctx,
                title=_("Missing Arguments"),
                description=_("You need to specify the Guild ID for the guild to lookup."),
            )

        if not await self.can_manage_playlist(scope, playlist, ctx, author, guild):
            return
        scope_name = humanize_scope(
            scope, ctx=guild if scope == PlaylistScope.GUILD.value else author
        )
        old_name = playlist.name
        update = {"name": new_name}
        await playlist.edit(update)
        msg = _("'{old}' playlist has been renamed to '{new}' (`{id}`) [**{scope}**]").format(
            old=bold(old_name), new=bold(playlist.name), id=playlist.id, scope=scope_name
        )
        await self._embed_msg(ctx, title=_("Playlist Modified"), description=msg)