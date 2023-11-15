def make_icon_url(info):
    if 'channel' in info and 'icon' in info:
        base_url = dirname(info['channel'])
        icon_fn = info['icon']
        # icon_cache_path = join(pkgs_dir, 'cache', icon_fn)
        # if isfile(icon_cache_path):
        #    return url_path(icon_cache_path)
        return '%s/icons/%s' % (base_url, icon_fn)
    return ''