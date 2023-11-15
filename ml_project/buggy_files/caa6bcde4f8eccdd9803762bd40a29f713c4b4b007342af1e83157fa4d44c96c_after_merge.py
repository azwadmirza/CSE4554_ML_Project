    async def _playlist_append(
        self,
        ctx: commands.Context,
        playlist_matches: PlaylistConverter,
        query: LazyGreedyConverter,
        *,
        scope_data: ScopeParser = None,
    ):
        """Add a track URL, playlist link, or quick search to a playlist.

        The track(s) will be appended to the end of the playlist.

        **Usage**:
        ​ ​ ​ ​ [p]playlist append playlist_name_OR_id track_name_OR_url args

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
        ​ ​ ​ ​ [p]playlist append MyGuildPlaylist Hello by Adele
        ​ ​ ​ ​ [p]playlist append MyGlobalPlaylist Hello by Adele --scope Global
        ​ ​ ​ ​ [p]playlist append MyGlobalPlaylist Hello by Adele --scope Global
        --Author Draper#6666
        """
        if scope_data is None:
            scope_data = [PlaylistScope.GUILD.value, ctx.author, ctx.guild, False]
        (scope, author, guild, specified_user) = scope_data
        if not await self._playlist_check(ctx):
            return
        try:
            (playlist_id, playlist_arg) = await self._get_correct_playlist_id(
                ctx, playlist_matches, scope, author, guild, specified_user
            )
        except TooManyMatches as e:
            return await self._embed_msg(ctx, title=str(e))
        if playlist_id is None:
            return await self._embed_msg(
                ctx,
                title=_("Playlist Not Found"),
                description=_("Could not match '{arg}' to a playlist").format(arg=playlist_arg),
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
                ctx,
                title=_("Missing Arguments"),
                description=_("You need to specify the Guild ID for the guild to lookup."),
            )

        if not await self.can_manage_playlist(scope, playlist, ctx, author, guild):
            return
        player = lavalink.get_player(ctx.guild.id)
        to_append = await self._playlist_tracks(
            ctx, player, audio_dataclasses.Query.process_input(query)
        )

        if isinstance(to_append, discord.Message):
            return None

        if not to_append:
            return await self._embed_msg(
                ctx, title=_("Could not find a track matching your query.")
            )
        track_list = playlist.tracks
        tracks_obj_list = playlist.tracks_obj
        to_append_count = len(to_append)
        scope_name = humanize_scope(
            scope, ctx=guild if scope == PlaylistScope.GUILD.value else author
        )
        appended = 0

        if to_append and to_append_count == 1:
            to = lavalink.Track(to_append[0])
            if to in tracks_obj_list:
                return await self._embed_msg(
                    ctx,
                    title=_("Skipping track"),
                    description=_(
                        "{track} is already in {playlist} (`{id}`) [**{scope}**]."
                    ).format(
                        track=to.title, playlist=playlist.name, id=playlist.id, scope=scope_name
                    ),
                )
            else:
                appended += 1
        if to_append and to_append_count > 1:
            to_append_temp = []
            for t in to_append:
                to = lavalink.Track(t)
                if to not in tracks_obj_list:
                    appended += 1
                    to_append_temp.append(t)
            to_append = to_append_temp
        if appended > 0:
            track_list.extend(to_append)
            update = {"tracks": track_list, "url": None}
            await playlist.edit(update)

        if to_append_count == 1 and appended == 1:
            track_title = to_append[0]["info"]["title"]
            return await self._embed_msg(
                ctx,
                title=_("Track added"),
                description=_("{track} appended to {playlist} (`{id}`) [**{scope}**].").format(
                    track=track_title, playlist=playlist.name, id=playlist.id, scope=scope_name
                ),
            )

        desc = _("{num} tracks appended to {playlist} (`{id}`) [**{scope}**].").format(
            num=appended, playlist=playlist.name, id=playlist.id, scope=scope_name
        )
        if to_append_count > appended:
            diff = to_append_count - appended
            desc += _("\n{existing} {plural} already in the playlist and were skipped.").format(
                existing=diff, plural=_("tracks are") if diff != 1 else _("track is")
            )

        embed = discord.Embed(title=_("Playlist Modified"), description=desc)
        await self._embed_msg(ctx, embed=embed)