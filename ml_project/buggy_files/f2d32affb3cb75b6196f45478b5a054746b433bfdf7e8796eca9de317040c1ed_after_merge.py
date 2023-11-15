    async def _playlist_list(self, ctx: commands.Context, *, scope_data: ScopeParser = None):
        """List saved playlists.

        **Usage**:
        ​ ​ ​ ​ [p]playlist list args

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
        ​ ​ ​ ​ [p]playlist list
        ​ ​ ​ ​ [p]playlist list --scope Global
        ​ ​ ​ ​ [p]playlist list --scope User
        """
        if scope_data is None:
            scope_data = [PlaylistScope.GUILD.value, ctx.author, ctx.guild, False]
        scope, author, guild, specified_user = scope_data

        try:
            playlists = await get_all_playlist(scope, self.bot, guild, author, specified_user)
        except MissingGuild:
            return await self._embed_msg(
                ctx,
                title=_("Missing Arguments"),
                description=_("You need to specify the Guild ID for the guild to lookup."),
            )

        if scope == PlaylistScope.GUILD.value:
            name = f"{guild.name}"
        elif scope == PlaylistScope.USER.value:
            name = f"{author}"
        else:
            name = "Global"

        if not playlists and specified_user:
            return await self._embed_msg(
                ctx,
                title=_("Playlist Not Found"),
                description=_("No saved playlists for {scope} created by {author}.").format(
                    scope=name, author=author
                ),
            )
        elif not playlists:
            return await self._embed_msg(
                ctx,
                title=_("Playlist Not Found"),
                description=_("No saved playlists for {scope}.").format(scope=name),
            )

        playlist_list = []
        space = "\N{EN SPACE}"
        for playlist in playlists:
            playlist_list.append(
                ("\n" + space * 4).join(
                    (
                        bold(playlist.name),
                        _("ID: {id}").format(id=playlist.id),
                        _("Tracks: {num}").format(num=len(playlist.tracks)),
                        _("Author: {name}\n").format(
                            name=self.bot.get_user(playlist.author)
                            or playlist.author
                            or _("Unknown")
                        ),
                    )
                )
            )
        abc_names = sorted(playlist_list, key=str.lower)
        len_playlist_list_pages = math.ceil(len(abc_names) / 5)
        playlist_embeds = []

        for page_num in range(1, len_playlist_list_pages + 1):
            embed = await self._build_playlist_list_page(ctx, page_num, abc_names, name)
            playlist_embeds.append(embed)
        await menu(ctx, playlist_embeds, DEFAULT_CONTROLS)