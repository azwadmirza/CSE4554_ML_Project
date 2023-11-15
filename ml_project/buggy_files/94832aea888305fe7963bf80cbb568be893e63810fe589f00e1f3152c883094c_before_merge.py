async def is_allowed(guild: discord.Guild, query: str):
    query = query.lower().strip()
    whitelist = set(await _config.guild(guild).url_keyword_whitelist())
    if whitelist:
        return any(i in query for i in whitelist)
    blacklist = set(await _config.guild(guild).url_keyword_blacklist())
    return not any(i in query for i in blacklist)