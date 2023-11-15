    async def _playlist_upload(self, ctx: commands.Context, *, scope_data: ScopeParser = None):
        """Uploads a playlist file as a playlist for the bot.

        V2 and old V3 playlist will be slow.
        V3 Playlist made with [p]playlist download will load a lot faster.

        **Usage**:
        ​ ​ ​ ​ [p]playlist upload args

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
        ​ ​ ​ ​ [p]playlist upload
        ​ ​ ​ ​ [p]playlist upload --scope Global
        ​ ​ ​ ​ [p]playlist upload --scope User
        """
        if scope_data is None:
            scope_data = [PlaylistScope.GUILD.value, ctx.author, ctx.guild, False]
        scope, author, guild, specified_user = scope_data
        temp_playlist = FakePlaylist(author.id, scope)
        if not await self.can_manage_playlist(scope, temp_playlist, ctx, author, guild):
            return

        if not await self._playlist_check(ctx):
            return
        player = lavalink.get_player(ctx.guild.id)

        await self._embed_msg(
            ctx,
            title=_(
                "Please upload the playlist file. Any other message will cancel this operation."
            ),
        )

        try:
            file_message = await ctx.bot.wait_for(
                "message", timeout=30.0, check=MessagePredicate.same_context(ctx)
            )
        except asyncio.TimeoutError:
            return await self._embed_msg(ctx, title=_("No file detected, try again later."))
        try:
            file_url = file_message.attachments[0].url
        except IndexError:
            return await self._embed_msg(ctx, title=_("Upload cancelled."))
        file_suffix = file_url.rsplit(".", 1)[1]
        if file_suffix != "txt":
            return await self._embed_msg(ctx, title=_("Only Red playlist files can be uploaded."))
        try:
            async with self.session.request("GET", file_url) as r:
                uploaded_playlist = await r.json(content_type="text/plain", encoding="utf-8")
        except UnicodeDecodeError:
            return await self._embed_msg(ctx, title=_("Not a valid playlist file."))

        new_schema = uploaded_playlist.get("schema", 1) >= 2
        version = uploaded_playlist.get("version", "v2")

        if new_schema and version == "v3":
            uploaded_playlist_url = uploaded_playlist.get("playlist_url", None)
            track_list = uploaded_playlist.get("tracks", [])
        else:
            uploaded_playlist_url = uploaded_playlist.get("link", None)
            track_list = uploaded_playlist.get("playlist", [])

        uploaded_playlist_name = uploaded_playlist.get(
            "name", (file_url.split("/")[6]).split(".")[0]
        )
        if (
            not uploaded_playlist_url
            or not match_yt_playlist(uploaded_playlist_url)
            or not (
                await self.music_cache.lavalink_query(
                    ctx, player, audio_dataclasses.Query.process_input(uploaded_playlist_url)
                )
            )[0].tracks
        ):
            if version == "v3":
                return await self._load_v3_playlist(
                    ctx,
                    scope,
                    uploaded_playlist_name,
                    uploaded_playlist_url,
                    track_list,
                    author,
                    guild,
                )
            return await self._load_v2_playlist(
                ctx,
                track_list,
                player,
                uploaded_playlist_url,
                uploaded_playlist_name,
                scope,
                author,
                guild,
            )
        return await ctx.invoke(
            self._playlist_save,
            playlist_name=uploaded_playlist_name,
            playlist_url=uploaded_playlist_url,
            scope_data=(scope, author, guild, specified_user),
        )