    async def _playlist_delete(
        self,
        ctx: commands.Context,
        playlist_matches: PlaylistConverter,
        *,
        scope_data: ScopeParser = None,
    ):
        """Delete a saved playlist.

        **Usage**:
        ​ ​ ​ ​ [p]playlist delete playlist_name_OR_id args

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
        ​ ​ ​ ​ [p]playlist delete MyGuildPlaylist
        ​ ​ ​ ​ [p]playlist delete MyGlobalPlaylist --scope Global
        ​ ​ ​ ​ [p]playlist delete MyPersonalPlaylist --scope User
        """
        if scope_data is None:
            scope_data = [PlaylistScope.GUILD.value, ctx.author, ctx.guild, False]
        scope, author, guild, specified_user = scope_data

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
                title=_("Playlist {id} does not exist in {scope} scope.").format(
                    id=playlist_id, scope=humanize_scope(scope, the=True)
                ),
            )
        except MissingGuild:
            return await self._embed_msg(
                ctx, title=_("You need to specify the Guild ID for the guild to lookup.")
            )

        if not await self.can_manage_playlist(scope, playlist, ctx, author, guild):
            return
        scope_name = humanize_scope(
            scope, ctx=guild if scope == PlaylistScope.GUILD.value else author
        )
        await delete_playlist(scope, playlist.id, guild or ctx.guild, author or ctx.author)

        await self._embed_msg(
            ctx,
            title=_("Playlist Deleted"),
            description=_("{name} (`{id}`) [**{scope}**] playlist deleted.").format(
                name=playlist.name, id=playlist.id, scope=scope_name
            ),
        )