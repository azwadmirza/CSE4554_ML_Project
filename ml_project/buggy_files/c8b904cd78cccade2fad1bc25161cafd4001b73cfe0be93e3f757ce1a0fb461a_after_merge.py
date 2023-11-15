    async def _playlist_copy(
        self,
        ctx: commands.Context,
        playlist_matches: PlaylistConverter,
        *,
        scope_data: ComplexScopeParser = None,
    ):

        """Copy a playlist from one scope to another.

        **Usage**:
        ​ ​ ​ ​ [p]playlist copy playlist_name_OR_id args

        **Args**:
        ​ ​ ​ ​ The following are all optional:
        ​ ​ ​ ​ ​ ​ ​ ​ --from-scope <scope>
        ​ ​ ​ ​ ​ ​ ​ ​ --from-author [user]
        ​ ​ ​ ​ ​ ​ ​ ​ --from-guild [guild] **Only the bot owner can use this**

        ​ ​ ​ ​ ​ ​ ​ ​ --to-scope <scope>
        ​ ​ ​ ​ ​ ​ ​ ​ --to-author [user]
        ​ ​ ​ ​ ​ ​ ​ ​ --to-guild [guild] **Only the bot owner can use this**

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
        ​ ​ ​ ​ [p]playlist copy MyGuildPlaylist --from-scope Guild --to-scope Global
        ​ ​ ​ ​ [p]playlist copy MyGlobalPlaylist --from-scope Global --to-author Draper#6666
        --to-scope User
        ​ ​ ​ ​ [p]playlist copy MyPersonalPlaylist --from-scope user --to-author Draper#6666
        --to-scope Guild --to-guild Red - Discord Bot
        """

        if scope_data is None:
            scope_data = [
                PlaylistScope.GUILD.value,
                ctx.author,
                ctx.guild,
                False,
                PlaylistScope.GUILD.value,
                ctx.author,
                ctx.guild,
                False,
            ]
        (
            from_scope,
            from_author,
            from_guild,
            specified_from_user,
            to_scope,
            to_author,
            to_guild,
            specified_to_user,
        ) = scope_data

        try:
            playlist_id, playlist_arg = await self._get_correct_playlist_id(
                ctx, playlist_matches, from_scope, from_author, from_guild, specified_from_user
            )
        except TooManyMatches as e:
            return await self._embed_msg(ctx, title=str(e))

        if playlist_id is None:
            return await self._embed_msg(
                ctx,
                title=_("Playlist Not Found"),
                description=_("Could not match '{arg}' to a playlist.").format(arg=playlist_arg),
            )

        temp_playlist = FakePlaylist(to_author.id, to_scope)
        if not await self.can_manage_playlist(to_scope, temp_playlist, ctx, to_author, to_guild):
            return

        try:
            from_playlist = await get_playlist(
                playlist_id, from_scope, self.bot, from_guild, from_author.id
            )
        except RuntimeError:
            return await self._embed_msg(
                ctx,
                title=_("Playlist Not Found"),
                description=_("Playlist {id} does not exist in {scope} scope.").format(
                    id=playlist_id, scope=humanize_scope(to_scope, the=True)
                ),
            )
        except MissingGuild:
            return await self._embed_msg(
                ctx, title=_("You need to specify the Guild ID for the guild to lookup.")
            )

        to_playlist = await create_playlist(
            ctx,
            to_scope,
            from_playlist.name,
            from_playlist.url,
            from_playlist.tracks,
            to_author,
            to_guild,
        )
        if to_scope == PlaylistScope.GLOBAL.value:
            to_scope_name = "the Global"
        elif to_scope == PlaylistScope.USER.value:
            to_scope_name = to_author
        else:
            to_scope_name = to_guild

        if from_scope == PlaylistScope.GLOBAL.value:
            from_scope_name = "the Global"
        elif from_scope == PlaylistScope.USER.value:
            from_scope_name = from_author
        else:
            from_scope_name = from_guild

        return await self._embed_msg(
            ctx,
            title=_("Playlist Copied"),
            description=_(
                "Playlist {name} (`{from_id}`) copied from {from_scope} to {to_scope} (`{to_id}`)."
            ).format(
                name=from_playlist.name,
                from_id=from_playlist.id,
                from_scope=humanize_scope(from_scope, ctx=from_scope_name, the=True),
                to_scope=humanize_scope(to_scope, ctx=to_scope_name, the=True),
                to_id=to_playlist.id,
            ),
        )