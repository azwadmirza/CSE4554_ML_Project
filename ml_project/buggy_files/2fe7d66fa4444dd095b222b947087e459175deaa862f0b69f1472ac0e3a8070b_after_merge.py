    async def _playlist_update(
        self,
        ctx: commands.Context,
        playlist_matches: PlaylistConverter,
        *,
        scope_data: ScopeParser = None,
    ):
        """Updates all tracks in a playlist.

        **Usage**:
        ​ ​ ​ ​ [p]playlist update playlist_name_OR_id args

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
        ​ ​ ​ ​ [p]playlist update MyGuildPlaylist
        ​ ​ ​ ​ [p]playlist update MyGlobalPlaylist --scope Global
        ​ ​ ​ ​ [p]playlist update MyPersonalPlaylist --scope User
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

        if not await self._playlist_check(ctx):
            return
        try:
            playlist = await get_playlist(playlist_id, scope, self.bot, guild, author)
            if not await self.can_manage_playlist(scope, playlist, ctx, author, guild):
                return
            if playlist.url:
                player = lavalink.get_player(ctx.guild.id)
                added, removed, playlist = await self._maybe_update_playlist(ctx, player, playlist)
            else:
                return await self._embed_msg(
                    ctx,
                    title=_("Invalid Playlist"),
                    description=_("Custom playlists cannot be updated."),
                )
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
        else:
            scope_name = humanize_scope(
                scope, ctx=guild if scope == PlaylistScope.GUILD.value else author
            )
            if added or removed:
                _colour = await ctx.embed_colour()
                removed_embeds = []
                added_embeds = []
                total_added = len(added)
                total_removed = len(removed)
                total_pages = math.ceil(total_removed / 10) + math.ceil(total_added / 10)
                page_count = 0
                if removed:
                    removed_text = ""
                    for i, track in enumerate(removed, 1):
                        if len(track.title) > 40:
                            track_title = str(track.title).replace("[", "")
                            track_title = "{}...".format((track_title[:40]).rstrip(" "))
                        else:
                            track_title = track.title
                        removed_text += f"`{i}.` **[{track_title}]({track.uri})**\n"
                        if i % 10 == 0 or i == total_removed:
                            page_count += 1
                            embed = discord.Embed(
                                title=_("Tracks removed"), colour=_colour, description=removed_text
                            )
                            text = _("Page {page_num}/{total_pages}").format(
                                page_num=page_count, total_pages=total_pages
                            )
                            embed.set_footer(text=text)
                            removed_embeds.append(embed)
                            removed_text = ""
                if added:
                    added_text = ""
                    for i, track in enumerate(added, 1):
                        if len(track.title) > 40:
                            track_title = str(track.title).replace("[", "")
                            track_title = "{}...".format((track_title[:40]).rstrip(" "))
                        else:
                            track_title = track.title
                        added_text += f"`{i}.` **[{track_title}]({track.uri})**\n"
                        if i % 10 == 0 or i == total_added:
                            page_count += 1
                            embed = discord.Embed(
                                title=_("Tracks added"), colour=_colour, description=added_text
                            )
                            text = _("Page {page_num}/{total_pages}").format(
                                page_num=page_count, total_pages=total_pages
                            )
                            embed.set_footer(text=text)
                            added_embeds.append(embed)
                            added_text = ""
                embeds = removed_embeds + added_embeds
                await menu(ctx, embeds, DEFAULT_CONTROLS)
            else:
                return await self._embed_msg(
                    ctx,
                    title=_("Playlist Has Not Been Modified"),
                    description=_("No changes for {name} (`{id}`) [**{scope}**].").format(
                        id=playlist.id, name=playlist.name, scope=scope_name
                    ),
                )