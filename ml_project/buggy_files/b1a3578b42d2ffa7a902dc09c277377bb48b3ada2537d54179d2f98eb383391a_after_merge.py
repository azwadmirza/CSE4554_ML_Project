    async def settings(self, ctx):
        """Show the current settings."""
        data = await self.config.guild(ctx.guild).all()
        global_data = await self.config.all()
        dj_role_obj = ctx.guild.get_role(data["dj_role"])
        dj_enabled = data["dj_enabled"]
        emptydc_enabled = data["emptydc_enabled"]
        emptydc_timer = data["emptydc_timer"]
        jukebox = data["jukebox"]
        jukebox_price = data["jukebox_price"]
        thumbnail = data["thumbnail"]
        jarbuild = redbot.core.__version__

        vote_percent = data["vote_percent"]
        msg = "----" + _("Server Settings") + "----\n"
        if emptydc_enabled:
            msg += _("Disconnect timer: [{num_seconds}]\n").format(
                num_seconds=self._dynamic_time(emptydc_timer)
            )
        if dj_enabled:
            msg += _("DJ Role:          [{role.name}]\n").format(role=dj_role_obj)
        if jukebox:
            msg += _("Jukebox:          [{jukebox_name}]\n").format(jukebox_name=jukebox)
            msg += _("Command price:    [{jukebox_price}]\n").format(jukebox_price=jukebox_price)
        msg += _(
            "Repeat:           [{repeat}]\n"
            "Shuffle:          [{shuffle}]\n"
            "Song notify msgs: [{notify}]\n"
            "Songs as status:  [{status}]\n"
        ).format(**global_data, **data)
        if thumbnail:
            msg += _("Thumbnails:       [{0}]\n").format(thumbnail)
        if vote_percent > 0:
            msg += _(
                "Vote skip:        [{vote_enabled}]\nSkip percentage:  [{vote_percent}%]\n"
            ).format(**data)
        msg += _(
            "---Lavalink Settings---\n"
            "Cog version:      [{version}]\n"
            "Jar build:        [{jarbuild}]\n"
            "External server:  [{use_external_lavalink}]"
        ).format(version=__version__, jarbuild=jarbuild, **global_data)

        embed = discord.Embed(colour=await ctx.embed_colour(), description=box(msg, lang="ini"))
        return await ctx.send(embed=embed)