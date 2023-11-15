def create_cache_dir():
    cache_dir = join(PackageCache.first_writable(context.pkgs_dirs).pkgs_dir, 'cache')
    mkdir_p_sudo_safe(cache_dir)
    return cache_dir