def package_cache():
    """
    Initializes the package cache. Each entry in the package cache
    dictionary contains three lists:
    - urls: the URLs used to refer to that package
    - files: the full pathnames to fetched copies of that package
    - dirs: the full pathnames to extracted copies of that package
    Nominally there should be no more than one entry in each list, but
    in theory this can handle the presence of multiple copies.
    """
    if package_cache_:
        return package_cache_
    # Stops recursion
    package_cache_['@'] = None
    for pdir in pkgs_dirs:
        try:
            data = open(join(pdir, 'urls.txt')).read()
            for url in data.split()[::-1]:
                if '/' in url:
                    add_cached_package(pdir, url)
        except IOError:
            pass
        if isdir(pdir):
            for fn in os.listdir(pdir):
                add_cached_package(pdir, fn)
    del package_cache_['@']
    return package_cache_