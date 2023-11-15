    async def _get_correct_playlist_id(
        self,
        context: commands.Context,
        matches: dict,
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
        original_input = matches.get("arg")
        correct_scope_matches = matches.get(scope)
        guild_to_query = guild.id
        user_to_query = author.id
        if not correct_scope_matches:
            return None, original_input
        if scope == PlaylistScope.USER.value:
            correct_scope_matches = [
                (i[2]["id"], i[2]["name"], len(i[2]["tracks"]), i[2]["author"])
                for i in correct_scope_matches
                if str(user_to_query) == i[0]
            ]
        elif scope == PlaylistScope.GUILD.value:
            if specified_user:
                correct_scope_matches = [
                    (i[2]["id"], i[2]["name"], len(i[2]["tracks"]), i[2]["author"])
                    for i in correct_scope_matches
                    if str(guild_to_query) == i[0] and i[2]["author"] == user_to_query
                ]
            else:
                correct_scope_matches = [
                    (i[2]["id"], i[2]["name"], len(i[2]["tracks"]), i[2]["author"])
                    for i in correct_scope_matches
                    if str(guild_to_query) == i[0]
                ]
        else:
            if specified_user:
                correct_scope_matches = [
                    (i[2]["id"], i[2]["name"], len(i[2]["tracks"]), i[2]["author"])
                    for i in correct_scope_matches
                    if i[2]["author"] == user_to_query
                ]
            else:
                correct_scope_matches = [
                    (i[2]["id"], i[2]["name"], len(i[2]["tracks"]), i[2]["author"])
                    for i in correct_scope_matches
                ]
        match_count = len(correct_scope_matches)
        # We done all the trimming we can with the info available time to ask the user
        if match_count > 10:
            if original_input.isnumeric():
                arg = int(original_input)
                correct_scope_matches = [
                    (i, n, t, a) for i, n, t, a in correct_scope_matches if i == arg
                ]
            if match_count > 10:
                raise TooManyMatches(
                    f"{match_count} playlists match {original_input}: "
                    f"Please try to be more specific, or use the playlist ID."
                )
        elif match_count == 1:
            return correct_scope_matches[0][0], original_input
        elif match_count == 0:
            return None, original_input

        # TODO : Convert this section to a new paged reaction menu when Toby Menus are Merged
        pos_len = 3
        playlists = f"{'#':{pos_len}}\n"

        for number, (pid, pname, ptracks, pauthor) in enumerate(correct_scope_matches, 1):
            author = self.bot.get_user(pauthor) or "Unknown"
            line = (
                f"{number}."
                f"    <{pname}>\n"
                f" - Scope:  < {humanize_scope(scope)} >\n"
                f" - ID:     < {pid} >\n"
                f" - Tracks: < {ptracks} >\n"
                f" - Author: < {author} >\n\n"
            )
            playlists += line

        embed = discord.Embed(
            title="Playlists found, which one would you like?",
            description=box(playlists, lang="md"),
            colour=await context.embed_colour(),
        )
        msg = await context.send(embed=embed)
        avaliable_emojis = ReactionPredicate.NUMBER_EMOJIS[1:]
        avaliable_emojis.append("🔟")
        emojis = avaliable_emojis[: len(correct_scope_matches)]
        emojis.append("❌")
        start_adding_reactions(msg, emojis)
        pred = ReactionPredicate.with_emojis(emojis, msg, user=context.author)
        try:
            await context.bot.wait_for("reaction_add", check=pred, timeout=60)
        except asyncio.TimeoutError:
            with contextlib.suppress(discord.HTTPException):
                await msg.delete()
            raise TooManyMatches(
                "Too many matches found and you did not select which one you wanted."
            )
        if emojis[pred.result] == "❌":
            with contextlib.suppress(discord.HTTPException):
                await msg.delete()
            raise TooManyMatches(
                "Too many matches found and you did not select which one you wanted."
            )
        with contextlib.suppress(discord.HTTPException):
            await msg.delete()
        return correct_scope_matches[pred.result][0], original_input