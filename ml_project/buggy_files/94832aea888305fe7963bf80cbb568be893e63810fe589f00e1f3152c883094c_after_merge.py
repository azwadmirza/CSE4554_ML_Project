async def is_allowed(guild: discord.Guild, query: str, query_obj: Query = None) -> bool:

    query = query.lower().strip()
    if query_obj is not None:
        query = query_obj.lavalink_query.replace("ytsearch:", "youtubesearch").replace(
            "scsearch:", "soundcloudsearch"
        )
    global_whitelist = set(await _config.url_keyword_whitelist())
    global_whitelist = [i.lower() for i in global_whitelist]
    if global_whitelist:
        return any(i in query for i in global_whitelist)
    global_blacklist = set(await _config.url_keyword_blacklist())
    global_blacklist = [i.lower() for i in global_blacklist]
    if any(i in query for i in global_blacklist):
        return False
    if guild is not None:
        whitelist = set(await _config.guild(guild).url_keyword_whitelist())
        whitelist = [i.lower() for i in whitelist]
        if whitelist:
            return any(i in query for i in whitelist)
        blacklist = set(await _config.guild(guild).url_keyword_blacklist())
        blacklist = [i.lower() for i in blacklist]
        return not any(i in query for i in blacklist)
    return True