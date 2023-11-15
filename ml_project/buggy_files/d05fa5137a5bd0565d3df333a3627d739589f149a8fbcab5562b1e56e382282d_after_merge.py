def mw_info(bot, trigger, found_match=None):
    """
    Retrives a snippet of the specified length from the given page on the given
    server.
    """
    match = found_match or trigger
    say_snippet(bot, match.group(1), unquote(match.group(2)), show_url=False)