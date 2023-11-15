def create_cache_dir():
    cache_dir = join(PackageCache.first_writable(context.pkgs_dirs).pkgs_dir, 'cache')
    try:
        makedirs(cache_dir)
    except OSError:
        pass
    return cache_dir