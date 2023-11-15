    async def _playlist_save(
        self,
        ctx: commands.Context,
        playlist_name: str,
        playlist_url: str,
        *,
        scope_data: ScopeParser = None,
    ):
        """Save a playlist from a url.

        **Usage**:
        ​ ​ ​ ​ [p]playlist save name url args

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
        ​ ​ ​ ​ [p]playlist save MyGuildPlaylist
        https://www.youtube.com/playlist?list=PLx0sYbCqOb8Q_CLZC2BdBSKEEB59BOPUM
        ​ ​ ​ ​ [p]playlist save MyGlobalPlaylist
        https://www.youtube.com/playlist?list=PLx0sYbCqOb8Q_CLZC2BdBSKEEB59BOPUM --scope Global
        ​ ​ ​ ​ [p]playlist save MyPersonalPlaylist
        https://open.spotify.com/playlist/1RyeIbyFeIJVnNzlGr5KkR --scope User
        """
        if scope_data is None:
            scope_data = [PlaylistScope.GUILD.value, ctx.author, ctx.guild, False]
        scope, author, guild, specified_user = scope_data
        scope_name = humanize_scope(
            scope, ctx=guild if scope == PlaylistScope.GUILD.value else author
        )

        temp_playlist = FakePlaylist(author.id, scope)
        if not await self.can_manage_playlist(scope, temp_playlist, ctx, author, guild):
            return ctx.command.reset_cooldown(ctx)
        playlist_name = playlist_name.split(" ")[0].strip('"')[:32]
        if playlist_name.isnumeric():
            ctx.command.reset_cooldown(ctx)
            return await self._embed_msg(
                ctx,
                title=_("Invalid Playlist Name"),
                description=_(
                    "Playlist names must be a single word (up to 32 "
                    "characters) and not numbers only."
                ),
            )
        if not await self._playlist_check(ctx):
            ctx.command.reset_cooldown(ctx)
            return
        player = lavalink.get_player(ctx.guild.id)
        tracklist = await self._playlist_tracks(
            ctx, player, audio_dataclasses.Query.process_input(playlist_url)
        )
        if isinstance(tracklist, discord.Message):
            return None
        if tracklist is not None:
            playlist = await create_playlist(
                ctx, scope, playlist_name, playlist_url, tracklist, author, guild
            )
            return await self._embed_msg(
                ctx,
                title=_("Playlist Created"),
                description=_(
                    "Playlist {name} (`{id}`) [**{scope}**] saved: {num} tracks added."
                ).format(name=playlist.name, num=len(tracklist), id=playlist.id, scope=scope_name),
            )