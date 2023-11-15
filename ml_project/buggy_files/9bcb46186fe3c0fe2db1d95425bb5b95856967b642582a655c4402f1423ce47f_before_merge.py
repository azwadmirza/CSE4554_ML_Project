    async def convert(self, ctx: commands.Context, arg: str) -> dict:
        global_scope = await _config.custom(PlaylistScope.GLOBAL.value).all()
        guild_scope = await _config.custom(PlaylistScope.GUILD.value).all()
        user_scope = await _config.custom(PlaylistScope.USER.value).all()
        user_matches = [
            (uid, pid, pdata)
            for uid, data in user_scope.items()
            for pid, pdata in data.items()
            if arg == pid or arg.lower() in pdata.get("name", "").lower()
        ]
        guild_matches = [
            (gid, pid, pdata)
            for gid, data in guild_scope.items()
            for pid, pdata in data.items()
            if arg == pid or arg.lower() in pdata.get("name", "").lower()
        ]
        global_matches = [
            (None, pid, pdata)
            for pid, pdata in global_scope.items()
            if arg == pid or arg.lower() in pdata.get("name", "").lower()
        ]
        if not user_matches and not guild_matches and not global_matches:
            raise commands.BadArgument(_("Could not match '{}' to a playlist.").format(arg))

        return {
            PlaylistScope.GLOBAL.value: global_matches,
            PlaylistScope.GUILD.value: guild_matches,
            PlaylistScope.USER.value: user_matches,
            "arg": arg,
        }