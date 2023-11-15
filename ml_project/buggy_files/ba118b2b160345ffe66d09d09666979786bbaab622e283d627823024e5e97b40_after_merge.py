    async def convert(self, ctx: commands.Context, arg: str) -> MutableMapping:
        """Get playlist for all scopes that match the argument user provided"""
        cog = ctx.cog
        user_matches = []
        guild_matches = []
        global_matches = []
        if cog:
            global_matches = await get_all_playlist_converter(
                PlaylistScope.GLOBAL.value,
                ctx.bot,
                cog.playlist_api,
                arg,
                guild=ctx.guild,
                author=ctx.author,
            )
            guild_matches = await get_all_playlist_converter(
                PlaylistScope.GUILD.value,
                ctx.bot,
                cog.playlist_api,
                arg,
                guild=ctx.guild,
                author=ctx.author,
            )
            user_matches = await get_all_playlist_converter(
                PlaylistScope.USER.value,
                ctx.bot,
                cog.playlist_api,
                arg,
                guild=ctx.guild,
                author=ctx.author,
            )
        if not user_matches and not guild_matches and not global_matches:
            raise commands.BadArgument(_("Could not match '{}' to a playlist.").format(arg))
        return {
            PlaylistScope.GLOBAL.value: global_matches,
            PlaylistScope.GUILD.value: guild_matches,
            PlaylistScope.USER.value: user_matches,
            "all": [*global_matches, *guild_matches, *user_matches],
            "arg": arg,
        }