def _first_writable_envs_dir():
    # Starting in conda 4.3, we use the writability test on '..../pkgs/url.txt' to determine
    # writability of '..../envs'.
    from ..core.package_cache import PackageCache
    for envs_dir in context.envs_dirs:
        pkgs_dir = join(dirname(envs_dir), 'pkgs')
        if PackageCache(pkgs_dir).is_writable:
            return envs_dir

    from ..exceptions import NotWritableError
    raise NotWritableError(context.envs_dirs[0], None)