def url_check(url) -> bool:
    valid_tld = [
        "youtube.com",
        "youtu.be",
        "soundcloud.com",
        "bandcamp.com",
        "vimeo.com",
        "beam.pro",
        "mixer.com",
        "twitch.tv",
        "spotify.com",
        "localtracks",
    ]
    query_url = urlparse(url)
    url_domain = ".".join(query_url.netloc.split(".")[-2:])
    if not query_url.netloc:
        url_domain = ".".join(query_url.path.split("/")[0].split(".")[-2:])
    return True if url_domain in valid_tld else False