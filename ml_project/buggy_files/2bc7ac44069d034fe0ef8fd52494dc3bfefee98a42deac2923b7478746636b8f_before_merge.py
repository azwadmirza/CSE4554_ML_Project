    async def _load_v2_playlist(
        self,
        ctx: commands.Context,
        uploaded_track_list,
        player: lavalink.player_manager.Player,
        playlist_url: str,
        uploaded_playlist_name: str,
        scope: str,
        author: Union[discord.User, discord.Member],
        guild: Union[discord.Guild],
    ):
        track_list = []
        track_count = 0
        successfull_count = 0
        uploaded_track_count = len(uploaded_track_list)

        embed1 = discord.Embed(
            colour=await ctx.embed_colour(), title=_("Please wait, adding tracks...")
        )
        playlist_msg = await ctx.send(embed=embed1)
        notifier = Notifier(ctx, playlist_msg, {"playlist": _("Loading track {num}/{total}...")})
        for song_url in uploaded_track_list:
            track_count += 1
            try:
                result, called_api = await self.music_cache.lavalink_query(
                    ctx, player, audio_dataclasses.Query.process_input(song_url)
                )
                track = result.tracks
            except Exception:
                continue
            try:
                track_obj = track_creator(player, other_track=track[0])
                track_list.append(track_obj)
                successfull_count += 1
            except Exception:
                continue
            if (track_count % 2 == 0) or (track_count == len(uploaded_track_list)):
                await notifier.notify_user(
                    current=track_count, total=len(uploaded_track_list), key="playlist"
                )

        playlist = await create_playlist(
            ctx, scope, uploaded_playlist_name, playlist_url, track_list, author, guild
        )
        scope_name = humanize_scope(
            scope, ctx=guild if scope == PlaylistScope.GUILD.value else author
        )
        if not successfull_count:
            msg = _("Empty playlist {name} (`{id}`) [**{scope}**] created.").format(
                name=playlist.name, id=playlist.id, scope=scope_name
            )
        elif uploaded_track_count != successfull_count:
            bad_tracks = uploaded_track_count - successfull_count
            msg = _(
                "Added {num} tracks from the {playlist_name} playlist. {num_bad} track(s) "
                "could not be loaded."
            ).format(num=successfull_count, playlist_name=playlist.name, num_bad=bad_tracks)
        else:
            msg = _("Added {num} tracks from the {playlist_name} playlist.").format(
                num=successfull_count, playlist_name=playlist.name
            )
        embed3 = discord.Embed(
            colour=await ctx.embed_colour(), title=_("Playlist Saved"), description=msg
        )
        await playlist_msg.edit(embed=embed3)