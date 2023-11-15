    async def can_manage_playlist(
        self, scope: str, playlist: Playlist, ctx: commands.Context, user, guild
    ):

        is_owner = await ctx.bot.is_owner(ctx.author)
        has_perms = False
        user_to_query = user
        guild_to_query = guild
        dj_enabled = None
        playlist_author = (
            guild.get_member(playlist.author)
            if guild
            else self.bot.get_user(playlist.author) or user
        )

        is_different_user = len({playlist.author, user_to_query.id, ctx.author.id}) != 1
        is_different_guild = True if guild_to_query is None else ctx.guild.id != guild_to_query.id

        if is_owner:
            has_perms = True
        elif playlist.scope == PlaylistScope.USER.value:
            if not is_different_user:
                has_perms = True
        elif playlist.scope == PlaylistScope.GUILD.value:
            if not is_different_guild:
                dj_enabled = self._dj_status_cache.setdefault(
                    ctx.guild.id, await self.config.guild(ctx.guild).dj_enabled()
                )
                if guild.owner_id == ctx.author.id:
                    has_perms = True
                elif dj_enabled and await self._has_dj_role(ctx, ctx.author):
                    has_perms = True
                elif await ctx.bot.is_mod(ctx.author):
                    has_perms = True
                elif not dj_enabled and not is_different_user:
                    has_perms = True

        if has_perms is False:
            if hasattr(playlist, "name"):
                msg = _(
                    "You do not have the permissions to manage {name} (`{id}`) [**{scope}**]."
                ).format(
                    user=playlist_author,
                    name=playlist.name,
                    id=playlist.id,
                    scope=humanize_scope(
                        playlist.scope,
                        ctx=guild_to_query
                        if playlist.scope == PlaylistScope.GUILD.value
                        else playlist_author
                        if playlist.scope == PlaylistScope.USER.value
                        else None,
                    ),
                )
            elif playlist.scope == PlaylistScope.GUILD.value and (
                is_different_guild or dj_enabled
            ):
                msg = _(
                    "You do not have the permissions to manage that playlist in {guild}."
                ).format(guild=guild_to_query)
            elif (
                playlist.scope in [PlaylistScope.GUILD.value, PlaylistScope.USER.value]
                and is_different_user
            ):
                msg = _(
                    "You do not have the permissions to manage playlist owned by {user}."
                ).format(user=playlist_author)
            else:
                msg = _(
                    "You do not have the permissions to manage "
                    "playlists in {scope} scope.".format(scope=humanize_scope(scope, the=True))
                )

            await self._embed_msg(ctx, title=_("No access to playlist."), description=msg)
            return False
        return True