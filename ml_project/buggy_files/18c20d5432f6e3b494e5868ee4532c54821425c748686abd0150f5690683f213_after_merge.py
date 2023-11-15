    async def _playlist_info(
        self,
        ctx: commands.Context,
        playlist_matches: PlaylistConverter,
        *,
        scope_data: ScopeParser = None,
    ):
        """Retrieve information from a saved playlist.

        **Usage**:
        ​ ​ ​ ​ [p]playlist info playlist_name_OR_id args

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
        ​ ​ ​ ​ [p]playlist info MyGuildPlaylist
        ​ ​ ​ ​ [p]playlist info MyGlobalPlaylist --scope Global
        ​ ​ ​ ​ [p]playlist info MyPersonalPlaylist --scope User
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
        track_len = len(playlist.tracks)

        msg = "​"
        track_idx = 0
        if track_len > 0:
            spaces = "\N{EN SPACE}" * (len(str(len(playlist.tracks))) + 2)
            for track in playlist.tracks:
                track_idx = track_idx + 1
                query = audio_dataclasses.Query.process_input(track["info"]["uri"])
                if query.is_local:
                    if track["info"]["title"] != "Unknown title":
                        msg += "`{}.` **{} - {}**\n{}{}\n".format(
                            track_idx,
                            track["info"]["author"],
                            track["info"]["title"],
                            spaces,
                            query.to_string_user(),
                        )
                    else:
                        msg += "`{}.` {}\n".format(track_idx, query.to_string_user())
                else:
                    msg += "`{}.` **[{}]({})**\n".format(
                        track_idx, track["info"]["title"], track["info"]["uri"]
                    )

        else:
            msg = "No tracks."

        if not playlist.url:
            embed_title = _("Playlist info for {playlist_name} (`{id}`) [**{scope}**]:\n").format(
                playlist_name=playlist.name, id=playlist.id, scope=scope_name
            )
        else:
            embed_title = _(
                "Playlist info for {playlist_name} (`{id}`) [**{scope}**]:\nURL: {url}"
            ).format(
                playlist_name=playlist.name, url=playlist.url, id=playlist.id, scope=scope_name
            )

        page_list = []
        pages = list(pagify(msg, delims=["\n"], page_length=2000))
        total_pages = len(pages)
        for numb, page in enumerate(pages, start=1):
            embed = discord.Embed(
                colour=await ctx.embed_colour(), title=embed_title, description=page
            )
            author_obj = self.bot.get_user(playlist.author) or playlist.author or _("Unknown")
            embed.set_footer(
                text=_("Page {page}/{pages} | Author: {author_name} | {num} track(s)").format(
                    author_name=author_obj, num=track_len, pages=total_pages, page=numb
                )
            )
            page_list.append(embed)
        await menu(ctx, page_list, DEFAULT_CONTROLS)