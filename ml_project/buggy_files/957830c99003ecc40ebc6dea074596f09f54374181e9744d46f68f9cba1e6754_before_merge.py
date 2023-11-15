async def global_unique_guild_finder(ctx: commands.Context, arg: str) -> discord.Guild:
    bot: commands.Bot = ctx.bot
    _id = _match_id(arg)

    if _id is not None:
        guild: discord.Guild = bot.get_guild(_id)
        if guild is not None:
            return guild

    maybe_matches = []
    for obj in bot.guilds:
        if obj.name == arg or str(obj) == arg:
            maybe_matches.append(obj)

    if not maybe_matches:
        raise NoMatchesFound(
            _(
                '"{arg}" was not found. It must be the ID or '
                "complete name of a server which the bot can see."
            ).format(arg=arg)
        )
    elif len(maybe_matches) == 1:
        return maybe_matches[0]
    else:
        raise TooManyMatches(
            _(
                '"{arg}" does not refer to a unique server. '
                "Please use the ID for the server you're trying to specify."
            ).format(arg=arg)
        )