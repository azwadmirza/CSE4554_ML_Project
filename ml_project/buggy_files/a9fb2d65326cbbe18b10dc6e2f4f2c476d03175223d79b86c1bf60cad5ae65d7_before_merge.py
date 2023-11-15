    async def _playlist_remove(
        self,
        ctx: commands.Context,
        playlist_matches: PlaylistConverter,
        url: str,
        *,
        scope_data: ScopeParser = None,
    ):
        """Remove a track from a playlist by url.

         **Usage**:
        ​ ​ ​ ​ [p]playlist remove playlist_name_OR_id url args

        **Args**:
        ​ ​ ​ ​ The following are all optional:
        ​ ​ ​ ​ ​ ​ ​ ​ --scope <scope>
        ​ ​ ​ ​ ​ ​ ​ ​ --author [user]
        ​ ​ ​ ​ ​ ​ ​ ​ --guild [guild] **Only the bot owner can use this**

        Scope is one of the following:
        ​ ​ ​ ​ Global
        ​ ​ ​ ​ Guild
        ​ ​ ​ ​ User

        Author can be one of the following:
        ​ ​ ​ ​ User ID
        ​ ​ ​ ​ User Mention
        ​ ​ ​ ​ User Name#123

        Guild can be one of the following:
        ​ ​ ​ ​ Guild ID
        ​ ​ ​ ​ Exact guild name

        Example use:
        ​ ​ ​ ​ [p]playlist remove MyGuildPlaylist https://www.youtube.com/watch?v=MN3x-kAbgFU
        ​ ​ ​ ​ [p]playlist remove MyGlobalPlaylist https://www.youtube.com/watch?v=MN3x-kAbgFU
        --scope Global
        ​ ​ ​ ​ [p]playlist remove MyPersonalPlaylist https://www.youtube.com/watch?v=MN3x-kAbgFU
        --scope User
        """
        if scope_data is None:
            scope_data = [PlaylistScope.GUILD.value, ctx.author, ctx.guild, False]
        scope, author, guild, specified_user = scope_data
        scope_name = humanize_scope(
            scope, ctx=guild if scope == PlaylistScope.GUILD.value else author
        )

        try:
            playlist_id, playlist_arg = await self._get_correct_playlist_id(
                ctx, playlist_matches, scope, author, guild, specified_user
            )
        except TooManyMatches as e:
            return await self._embed_msg(ctx, str(e))
        if playlist_id is None:
            return await self._embed_msg(
                ctx, _("Could not match '{arg}' to a playlist.").format(arg=playlist_arg)
            )

        try:
            playlist = await get_playlist(playlist_id, scope, self.bot, guild, author)
        except RuntimeError:
            return await self._embed_msg(
                ctx,
                _("Playlist {id} does not exist in {scope} scope.").format(
                    id=playlist_id, scope=humanize_scope(scope, the=True)
                ),
            )
        except MissingGuild:
            return await self._embed_msg(
                ctx, _("You need to specify the Guild ID for the guild to lookup.")
            )

        if not await self.can_manage_playlist(scope, playlist, ctx, author, guild):
            return

        track_list = playlist.tracks
        clean_list = [track for track in track_list if url != track["info"]["uri"]]
        if len(track_list) == len(clean_list):
            return await self._embed_msg(ctx, _("URL not in playlist."))
        del_count = len(track_list) - len(clean_list)
        if not clean_list:
            await delete_playlist(
                scope=playlist.scope, playlist_id=playlist.id, guild=guild, author=playlist.author
            )
            return await self._embed_msg(ctx, _("No tracks left, removing playlist."))
        update = {"tracks": clean_list, "url": None}
        await playlist.edit(update)
        if del_count > 1:
            await self._embed_msg(
                ctx,
                _(
                    "{num} entries have been removed from the"
                    " playlist {playlist_name} (`{id}`) [**{scope}**]."
                ).format(
                    num=del_count, playlist_name=playlist.name, id=playlist.id, scope=scope_name
                ),
            )
        else:
            await self._embed_msg(
                ctx,
                _(
                    "The track has been removed from the"
                    " playlist: {playlist_name} (`{id}`) [**{scope}**]."
                ).format(playlist_name=playlist.name, id=playlist.id, scope=scope_name),
            )