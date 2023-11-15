def match_yt_playlist(url) -> bool:
    if _RE_YT_LIST_PLAYLIST.match(url):
        return True
    return False