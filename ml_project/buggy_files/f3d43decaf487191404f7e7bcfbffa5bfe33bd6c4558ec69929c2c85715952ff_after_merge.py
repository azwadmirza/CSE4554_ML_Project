    async def _playlist_remdupe(
        self,
        ctx: commands.Context,
        playlist_matches: PlaylistConverter,
        *,
        scope_data: ScopeParser = None,
    ):
        """Remove duplicate tracks from a saved playlist.

        **Usage**:
        ​ ​ ​ ​ [p]playlist dedupe playlist_name_OR_id args

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
        ​ ​ ​ ​ [p]playlist dedupe MyGuildPlaylist
        ​ ​ ​ ​ [p]playlist dedupe MyGlobalPlaylist --scope Global
        ​ ​ ​ ​ [p]playlist dedupe MyPersonalPlaylist --scope User
        """
        async with ctx.typing():
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
                return await self._embed_msg(ctx, title=str(e))
            if playlist_id is None:
                return await self._embed_msg(
                    ctx,
                    title=_("Playlist Not Found"),
                    description=_("Could not match '{arg}' to a playlist.").format(
                        arg=playlist_arg
                    ),
                )

            try:
                playlist = await get_playlist(playlist_id, scope, self.bot, guild, author)
            except RuntimeError:
                return await self._embed_msg(
                    ctx,
                    title=_("Playlist Not Found"),
                    description=_("Playlist {id} does not exist in {scope} scope.").format(
                        id=playlist_id, scope=humanize_scope(scope, the=True)
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

            track_objects = playlist.tracks_obj
            original_count = len(track_objects)
            unique_tracks = set()
            unique_tracks_add = unique_tracks.add
            track_objects = [
                x for x in track_objects if not (x in unique_tracks or unique_tracks_add(x))
            ]

            tracklist = []
            for track in track_objects:
                track_keys = track._info.keys()
                track_values = track._info.values()
                track_id = track.track_identifier
                track_info = {}
                for k, v in zip(track_keys, track_values):
                    track_info[k] = v
                keys = ["track", "info"]
                values = [track_id, track_info]
                track_obj = {}
                for key, value in zip(keys, values):
                    track_obj[key] = value
                tracklist.append(track_obj)

        final_count = len(tracklist)
        if original_count - final_count != 0:
            await self._embed_msg(
                ctx,
                title=_("Playlist Modified"),
                description=_(
                    "Removed {track_diff} duplicated "
                    "tracks from {name} (`{id}`) [**{scope}**] playlist."
                ).format(
                    name=playlist.name,
                    id=playlist.id,
                    track_diff=original_count - final_count,
                    scope=scope_name,
                ),
            )
        else:
            await self._embed_msg(
                ctx,
                title=_("Playlist Has Not Been Modified"),
                description=_(
                    "{name} (`{id}`) [**{scope}**] playlist has no duplicate tracks."
                ).format(name=playlist.name, id=playlist.id, scope=scope_name),
            )