    async def _get_correct_playlist_id(
        self,
        context: commands.Context,
        matches: MutableMapping,
        scope: str,
        author: discord.User,
        guild: discord.Guild,
        specified_user: bool = False,
    ) -> Tuple[Optional[int], str]:
        """
        Parameters
        ----------
        context: commands.Context
            The context in which this is being called.
        matches: dict
            A dict of the matches found where key is scope and value is matches.
        scope:str
            The custom config scope. A value from :code:`PlaylistScope`.
        author: discord.User
            The user.
        guild: discord.Guild
            The guild.
        specified_user: bool
            Whether or not a user ID was specified via argparse.
        Returns
        -------
        Tuple[Optional[int], str]
            Tuple of Playlist ID or None if none found and original user input.
        Raises
        ------
        `TooManyMatches`
            When more than 10 matches are found or
            When multiple matches are found but none is selected.

        """
        correct_scope_matches: List[Playlist]
        original_input = matches.get("arg")
        correct_scope_matches_temp: MutableMapping = matches.get(scope)
        guild_to_query = guild.id
        user_to_query = author.id
        if not correct_scope_matches_temp:
            return None, original_input
        if scope == PlaylistScope.USER.value:
            correct_scope_matches = [
                p for p in correct_scope_matches_temp if user_to_query == p.scope_id
            ]
        elif scope == PlaylistScope.GUILD.value:
            if specified_user:
                correct_scope_matches = [
                    p
                    for p in correct_scope_matches_temp
                    if guild_to_query == p.scope_id and p.author == user_to_query
                ]
            else:
                correct_scope_matches = [
                    p for p in correct_scope_matches_temp if guild_to_query == p.scope_id
                ]
        else:
            if specified_user:
                correct_scope_matches = [
                    p for p in correct_scope_matches_temp if p.author == user_to_query
                ]
            else:
                correct_scope_matches = [p for p in correct_scope_matches_temp]

        match_count = len(correct_scope_matches)
        if match_count > 1:
            correct_scope_matches2 = [
                p for p in correct_scope_matches if p.name == str(original_input).strip()
            ]
            if correct_scope_matches2:
                correct_scope_matches = correct_scope_matches2
            elif original_input.isnumeric():
                arg = int(original_input)
                correct_scope_matches3 = [p for p in correct_scope_matches if p.id == arg]
                if correct_scope_matches3:
                    correct_scope_matches = correct_scope_matches3
        match_count = len(correct_scope_matches)
        # We done all the trimming we can with the info available time to ask the user
        if match_count > 10:
            if original_input.isnumeric():
                arg = int(original_input)
                correct_scope_matches = [p for p in correct_scope_matches if p.id == arg]
            if match_count > 10:
                raise TooManyMatches(
                    _(
                        "{match_count} playlists match {original_input}: "
                        "Please try to be more specific, or use the playlist ID."
                    ).format(match_count=match_count, original_input=original_input)
                )
        elif match_count == 1:
            return correct_scope_matches[0].id, original_input
        elif match_count == 0:
            return None, original_input

        # TODO : Convert this section to a new paged reaction menu when Toby Menus are Merged
        pos_len = 3
        playlists = f"{'#':{pos_len}}\n"
        number = 0
        for number, playlist in enumerate(correct_scope_matches, 1):
            author = self.bot.get_user(playlist.author) or playlist.author or _("Unknown")
            line = _(
                "{number}."
                "    <{playlist.name}>\n"
                " - Scope:  < {scope} >\n"
                " - ID:     < {playlist.id} >\n"
                " - Tracks: < {tracks} >\n"
                " - Author: < {author} >\n\n"
            ).format(
                number=number,
                playlist=playlist,
                scope=humanize_scope(scope),
                tracks=len(playlist.tracks),
                author=author,
            )
            playlists += line

        embed = discord.Embed(
            title=_("{playlists} playlists found, which one would you like?").format(
                playlists=number
            ),
            description=box(playlists, lang="md"),
            colour=await context.embed_colour(),
        )
        msg = await context.send(embed=embed)
        avaliable_emojis = ReactionPredicate.NUMBER_EMOJIS[1:]
        avaliable_emojis.append("🔟")
        emojis = avaliable_emojis[: len(correct_scope_matches)]
        emojis.append("\N{CROSS MARK}")
        start_adding_reactions(msg, emojis)
        pred = ReactionPredicate.with_emojis(emojis, msg, user=context.author)
        try:
            await context.bot.wait_for("reaction_add", check=pred, timeout=60)
        except asyncio.TimeoutError:
            with contextlib.suppress(discord.HTTPException):
                await msg.delete()
            raise TooManyMatches(
                _("Too many matches found and you did not select which one you wanted.")
            )
        if emojis[pred.result] == "\N{CROSS MARK}":
            with contextlib.suppress(discord.HTTPException):
                await msg.delete()
            raise TooManyMatches(
                _("Too many matches found and you did not select which one you wanted.")
            )
        with contextlib.suppress(discord.HTTPException):
            await msg.delete()
        return correct_scope_matches[pred.result].id, original_input