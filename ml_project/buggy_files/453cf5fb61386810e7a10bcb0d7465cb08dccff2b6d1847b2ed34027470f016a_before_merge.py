async def global_unique_user_finder(
    ctx: commands.Context, arg: str, guild: discord.guild = None
) -> discord.abc.User:
    bot: commands.Bot = ctx.bot
    guild = guild or ctx.guild
    _id = _match_id(arg)

    if _id is not None:
        user: discord.User = bot.get_user(_id)
        if user is not None:
            return user

    objects = bot.users

    maybe_matches = []
    for obj in objects:
        if obj.name == arg or str(obj) == arg:
            maybe_matches.append(obj)

    if guild is not None:
        for member in guild.members:
            if member.nick == arg and not any(obj.id == member.id for obj in maybe_matches):
                maybe_matches.append(member)

    if not maybe_matches:
        raise NoMatchesFound(
            _(
                '"{arg}" was not found. It must be the ID or name or '
                "mention a user which the bot can see."
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