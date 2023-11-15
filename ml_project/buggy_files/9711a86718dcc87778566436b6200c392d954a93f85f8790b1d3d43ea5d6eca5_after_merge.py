def normalize_urls(urls, platform=None, offline_only=False):
    defaults = tuple(x.rstrip('/') + '/' for x in get_default_urls())
    alias = binstar_channel_alias(channel_alias)
    newurls = []
    while urls:
        url = urls[0]
        urls = urls[1:]
        if url == "system" and rc_path:
            urls = get_rc_urls() + urls
            continue
        elif url in ("defaults", "system"):
            t_urls = defaults
        elif url == "local":
            t_urls = get_local_urls()
        else:
            t_urls = [url]
        for url0 in t_urls:
            url0 = url0.rstrip('/')
            if not is_url(url0):
                url0 = alias + url0
            if offline_only and not url0.startswith('file:'):
                continue
            for plat in (platform or subdir, 'noarch'):
                newurls.append('%s/%s/' % (url0, plat))
    return newurls