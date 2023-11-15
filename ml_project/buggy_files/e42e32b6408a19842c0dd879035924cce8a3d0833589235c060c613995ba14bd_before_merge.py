def match_yt_playlist(url):
    if re_yt_list_playlist.match(url):
        return True
    return False