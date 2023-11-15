    async def _playlist_queue(
        self, ctx: commands.Context, playlist_name: str, *, scope_data: ScopeParser = None
    ):
        """Save the queue to a playlist.

        **Usage**:
        ​ ​ ​ ​ [p]playlist queue playlist_name

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
        ​ ​ ​ ​ [p]playlist queue MyGuildPlaylist
        ​ ​ ​ ​ [p]playlist queue MyGlobalPlaylist --scope Global
        ​ ​ ​ ​ [p]playlist queue MyPersonalPlaylist --scope User
        """
        if scope_data is None:
            scope_data = [PlaylistScope.GUILD.value, ctx.author, ctx.guild, False]
        scope, author, guild, specified_user = scope_data
        scope_name = humanize_scope(
            scope, ctx=guild if scope == PlaylistScope.GUILD.value else author
        )
        temp_playlist = FakePlaylist(author.id, scope)
        if not await self.can_manage_playlist(scope, temp_playlist, ctx, author, guild):
            ctx.command.reset_cooldown(ctx)
            return
        playlist_name = playlist_name.split(" ")[0].strip('"')[:32]
        if playlist_name.isnumeric():
            ctx.command.reset_cooldown(ctx)
            return await self._embed_msg(
                ctx,
                title=_("Invalid Playlist Name"),
                description=_(
                    "Playlist names must be a single word "
                    "(up to 32 characters) and not numbers only."
                ),
            )
        if not self._player_check(ctx):
            ctx.command.reset_cooldown(ctx)
            return await self._embed_msg(ctx, title=_("Nothing playing."))

        player = lavalink.get_player(ctx.guild.id)
        if not player.queue:
            ctx.command.reset_cooldown(ctx)
            return await self._embed_msg(ctx, title=_("There's nothing in the queue."))
        tracklist = []
        np_song = track_creator(player, "np")
        tracklist.append(np_song)
        for track in player.queue:
            queue_idx = player.queue.index(track)
            track_obj = track_creator(player, queue_idx)
            tracklist.append(track_obj)

        playlist = await create_playlist(ctx, scope, playlist_name, None, tracklist, author, guild)
        await self._embed_msg(
            ctx,
            title=_("Playlist Created"),
            description=_(
                "Playlist {name} (`{id}`) [**{scope}**] "
                "saved from current queue: {num} tracks added."
            ).format(
                name=playlist.name, num=len(playlist.tracks), id=playlist.id, scope=scope_name
            ),
        )