def generate_youtube_url(raw_song, meta_tags):
    url_fetch = GenerateYouTubeURL(raw_song, meta_tags)
    if const.args.youtube_api_key:
        url = url_fetch.api()
    else:
        url = url_fetch.scrape()
    return url