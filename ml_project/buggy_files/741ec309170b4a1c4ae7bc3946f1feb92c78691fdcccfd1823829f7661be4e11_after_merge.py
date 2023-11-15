    async def _playlist_start(
        self,
        ctx: commands.Context,
        playlist_matches: PlaylistConverter,
        *,
        scope_data: ScopeParser = None,
    ):
        """Load a playlist into the queue.

        **Usage**:
        ​ ​ ​ ​ [p]playlist start playlist_name_OR_id args

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
        ​ ​ ​ ​ [p]playlist start MyGuildPlaylist
        ​ ​ ​ ​ [p]playlist start MyGlobalPlaylist --scope Global
        ​ ​ ​ ​ [p]playlist start MyPersonalPlaylist --scope User
        """
        if scope_data is None:
            scope_data = [PlaylistScope.GUILD.value, ctx.author, ctx.guild, False]
        scope, author, guild, specified_user = scope_data
        dj_enabled = self._dj_status_cache.setdefault(
            ctx.guild.id, await self.config.guild(ctx.guild).dj_enabled()
        )
        if dj_enabled:
            if not await self._can_instaskip(ctx, ctx.author):
                await self._embed_msg(
                    ctx,
                    title=_("Unable To Play Tracks"),
                    description=_("You need the DJ role to start playing playlists."),
                )
                return False

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
                description=_("Could not match '{arg}' to a playlist").format(arg=playlist_arg),
            )

        if not await self._playlist_check(ctx):
            return
        jukebox_price = await self.config.guild(ctx.guild).jukebox_price()
        if not await self._currency_check(ctx, jukebox_price):
            return
        maxlength = await self.config.guild(ctx.guild).maxlength()
        author_obj = self.bot.get_user(ctx.author.id)
        track_len = 0
        playlist = None
        try:
            playlist = await get_playlist(playlist_id, scope, self.bot, guild, author)
            player = lavalink.get_player(ctx.guild.id)
            tracks = playlist.tracks_obj
            empty_queue = not player.queue
            for track in tracks:
                if not await is_allowed(
                    ctx.guild,
                    (
                        f"{track.title} {track.author} {track.uri} "
                        f"{str(audio_dataclasses.Query.process_input(track))}"
                    ),
                ):
                    log.debug(f"Query is not allowed in {ctx.guild} ({ctx.guild.id})")
                    continue
                query = audio_dataclasses.Query.process_input(track.uri)
                if query.is_local:
                    local_path = audio_dataclasses.LocalPath(track.uri)
                    if not await self._localtracks_check(ctx):
                        pass
                    if not local_path.exists() and not local_path.is_file():
                        continue
                if maxlength > 0:
                    if not track_limit(track.length, maxlength):
                        continue

                player.add(author_obj, track)
                self.bot.dispatch(
                    "red_audio_track_enqueue", player.channel.guild, track, ctx.author
                )
                track_len += 1
            player.maybe_shuffle(0 if empty_queue else 1)
            if len(tracks) > track_len:
                maxlength_msg = " {bad_tracks} tracks cannot be queued.".format(
                    bad_tracks=(len(tracks) - track_len)
                )
            else:
                maxlength_msg = ""
            if scope == PlaylistScope.GUILD.value:
                scope_name = f"{guild.name}"
            elif scope == PlaylistScope.USER.value:
                scope_name = f"{author}"
            else:
                scope_name = "Global"

            embed = discord.Embed(
                title=_("Playlist Enqueued"),
                description=_(
                    "{name} - (`{id}`) [**{scope}**]\nAdded {num} "
                    "tracks to the queue.{maxlength_msg}"
                ).format(
                    num=track_len,
                    maxlength_msg=maxlength_msg,
                    name=playlist.name,
                    id=playlist.id,
                    scope=scope_name,
                ),
            )
            await self._embed_msg(ctx, embed=embed)
            if not player.current:
                await player.play()
            return
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
        except TypeError:
            if playlist:
                return await ctx.invoke(self.play, query=playlist.url)