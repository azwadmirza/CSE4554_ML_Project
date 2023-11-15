    async def settings(self, ctx: commands.Context):
        """Show the current settings."""
        is_owner = await ctx.bot.is_owner(ctx.author)
        global_data = await self.config.all()
        data = await self.config.guild(ctx.guild).all()
        dj_role_obj = ctx.guild.get_role(data["dj_role"])
        dj_enabled = data["dj_enabled"]
        emptydc_enabled = data["emptydc_enabled"]
        emptydc_timer = data["emptydc_timer"]
        emptypause_enabled = data["emptypause_enabled"]
        emptypause_timer = data["emptypause_timer"]
        jukebox = data["jukebox"]
        jukebox_price = data["jukebox_price"]
        thumbnail = data["thumbnail"]
        dc = data["disconnect"]
        autoplay = data["auto_play"]
        maxlength = data["maxlength"]
        vote_percent = data["vote_percent"]
        current_level = CacheLevel(global_data["cache_level"])
        song_repeat = _("Enabled") if data["repeat"] else _("Disabled")
        song_shuffle = _("Enabled") if data["shuffle"] else _("Disabled")
        song_notify = _("Enabled") if data["notify"] else _("Disabled")
        song_status = _("Enabled") if global_data["status"] else _("Disabled")

        spotify_cache = CacheLevel.set_spotify()
        youtube_cache = CacheLevel.set_youtube()
        lavalink_cache = CacheLevel.set_lavalink()
        has_spotify_cache = current_level.is_superset(spotify_cache)
        has_youtube_cache = current_level.is_superset(youtube_cache)
        has_lavalink_cache = current_level.is_superset(lavalink_cache)
        autoplaylist = data["autoplaylist"]
        vote_enabled = data["vote_enabled"]
        msg = "----" + _("Server Settings") + "----        \n"
        msg += _("Auto-disconnect:  [{dc}]\n").format(dc=_("Enabled") if dc else _("Disabled"))
        msg += _("Auto-play:        [{autoplay}]\n").format(
            autoplay=_("Enabled") if autoplay else _("Disabled")
        )
        if emptydc_enabled:
            msg += _("Disconnect timer: [{num_seconds}]\n").format(
                num_seconds=dynamic_time(emptydc_timer)
            )
        if emptypause_enabled:
            msg += _("Auto Pause timer: [{num_seconds}]\n").format(
                num_seconds=dynamic_time(emptypause_timer)
            )
        if dj_enabled and dj_role_obj:
            msg += _("DJ Role:          [{role.name}]\n").format(role=dj_role_obj)
        if jukebox:
            msg += _("Jukebox:          [{jukebox_name}]\n").format(jukebox_name=jukebox)
            msg += _("Command price:    [{jukebox_price}]\n").format(
                jukebox_price=humanize_number(jukebox_price)
            )
        if maxlength > 0:
            msg += _("Max track length: [{tracklength}]\n").format(
                tracklength=dynamic_time(maxlength)
            )
        msg += _(
            "Repeat:           [{repeat}]\n"
            "Shuffle:          [{shuffle}]\n"
            "Song notify msgs: [{notify}]\n"
            "Songs as status:  [{status}]\n"
        ).format(repeat=song_repeat, shuffle=song_shuffle, notify=song_notify, status=song_status)
        if thumbnail:
            msg += _("Thumbnails:       [{0}]\n").format(
                _("Enabled") if thumbnail else _("Disabled")
            )
        if vote_percent > 0:
            msg += _(
                "Vote skip:        [{vote_enabled}]\nSkip percentage:  [{vote_percent}%]\n"
            ).format(
                vote_percent=vote_percent,
                vote_enabled=_("Enabled") if vote_enabled else _("Disabled"),
            )

        if self.owns_autoplay is not None:
            msg += (
                "\n---"
                + _("Auto-play Settings")
                + "---        \n"
                + _("Owning Cog:       [{name}]\n").format(name=self._cog_name)
            )
        elif autoplay or autoplaylist["enabled"]:
            if autoplaylist["enabled"]:
                pname = autoplaylist["name"]
                pid = autoplaylist["id"]
                pscope = autoplaylist["scope"]
                if pscope == PlaylistScope.GUILD.value:
                    pscope = f"Server"
                elif pscope == PlaylistScope.USER.value:
                    pscope = f"User"
                else:
                    pscope = "Global"
            else:
                pname = _("Cached")
                pid = _("Cached")
                pscope = _("Cached")
            msg += (
                "\n---"
                + _("Auto-play Settings")
                + "---        \n"
                + _("Playlist name:    [{pname}]\n")
                + _("Playlist ID:      [{pid}]\n")
                + _("Playlist scope:   [{pscope}]\n")
            ).format(pname=pname, pid=pid, pscope=pscope)

        if is_owner:
            msg += (
                "\n---"
                + _("Cache Settings")
                + "---        \n"
                + _("Max age:          [{max_age}]\n")
                + _("Spotify cache:    [{spotify_status}]\n")
                + _("Youtube cache:    [{youtube_status}]\n")
                + _("Lavalink cache:   [{lavalink_status}]\n")
            ).format(
                max_age=str(await self.config.cache_age()) + " " + _("days"),
                spotify_status=_("Enabled") if has_spotify_cache else _("Disabled"),
                youtube_status=_("Enabled") if has_youtube_cache else _("Disabled"),
                lavalink_status=_("Enabled") if has_lavalink_cache else _("Disabled"),
            )

        msg += _(
            "\n---" + _("Lavalink Settings") + "---        \n"
            "Cog version:      [{version}]\n"
            "Red-Lavalink:     [{redlava}]\n"
            "External server:  [{use_external_lavalink}]\n"
        ).format(
            version=__version__,
            redlava=lavalink.__version__,
            use_external_lavalink=_("Enabled")
            if global_data["use_external_lavalink"]
            else _("Disabled"),
        )
        if is_owner:
            msg += _("Localtracks path: [{localpath}]\n").format(**global_data)

        embed = discord.Embed(colour=await ctx.embed_colour(), description=box(msg, lang="ini"))
        return await ctx.send(embed=embed)