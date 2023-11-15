    async def _load_v3_playlist(
        self,
        ctx: commands.Context,
        scope: str,
        uploaded_playlist_name: str,
        uploaded_playlist_url: str,
        track_list,
        author: Union[discord.User, discord.Member],
        guild: Union[discord.Guild],
    ):
        embed1 = discord.Embed(
            colour=await ctx.embed_colour(), title=_("Please wait, adding tracks...")
        )
        playlist_msg = await ctx.send(embed=embed1)
        track_count = len(track_list)
        uploaded_track_count = len(track_list)
        await asyncio.sleep(1)
        embed2 = discord.Embed(
            colour=await ctx.embed_colour(),
            title=_("Loading track {num}/{total}...").format(
                num=track_count, total=uploaded_track_count
            ),
        )
        await playlist_msg.edit(embed=embed2)
        playlist = await create_playlist(
            ctx, scope, uploaded_playlist_name, uploaded_playlist_url, track_list, author, guild
        )
        scope_name = humanize_scope(
            scope, ctx=guild if scope == PlaylistScope.GUILD.value else author
        )
        if not track_count:
            msg = _("Empty playlist {name} (`{id}`) [**{scope}**] created.").format(
                name=playlist.name, id=playlist.id, scope=scope_name
            )
        elif uploaded_track_count != track_count:
            bad_tracks = uploaded_track_count - track_count
            msg = _(
                "Added {num} tracks from the {playlist_name} playlist. {num_bad} track(s) "
                "could not be loaded."
            ).format(num=track_count, playlist_name=playlist.name, num_bad=bad_tracks)
        else:
            msg = _("Added {num} tracks from the {playlist_name} playlist.").format(
                num=track_count, playlist_name=playlist.name
            )
        embed3 = discord.Embed(
            colour=await ctx.embed_colour(), title=_("Playlist Saved"), description=msg
        )
        await playlist_msg.edit(embed=embed3)
        database_entries = []
        time_now = str(datetime.datetime.now(datetime.timezone.utc))
        for t in track_list:
            uri = t.get("info", {}).get("uri")
            if uri:
                t = {"loadType": "V2_COMPAT", "tracks": [t], "query": uri}
                database_entries.append(
                    {
                        "query": uri,
                        "data": json.dumps(t),
                        "last_updated": time_now,
                        "last_fetched": time_now,
                    }
                )
        if database_entries and HAS_SQL:
            await self.music_cache.insert("lavalink", database_entries)