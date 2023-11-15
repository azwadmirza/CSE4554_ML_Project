def normalize_urls(urls, platform=None, offline_only=False):
    platform = platform or subdir
    defaults = tuple(x.rstrip('/') + '/' for x in get_default_urls())
    alias = binstar_channel_alias(channel_alias)

    def normalize_(url):
        url = url.rstrip('/')
        if is_url(url):
            url_s = canonical_channel_name(url, True)
        else:
            url_s = url
            url = alias + url
        return url_s, url
    newurls = OrderedDict()
    priority = 0
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
        priority += 1
        for url0 in t_urls:
            url_s, url0 = normalize_(url0)
            if offline_only and not url0.startswith('file:'):
                continue
            for plat in (platform, 'noarch'):
                newurls.setdefault('%s/%s/' % (url0, plat), (url_s, priority))
    return newurls