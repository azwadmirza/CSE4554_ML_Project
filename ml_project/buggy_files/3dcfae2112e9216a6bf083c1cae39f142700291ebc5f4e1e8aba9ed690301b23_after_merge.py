def setup_node_modules(
    production: bool = DEFAULT_PRODUCTION,
    prefer_offline: bool = False,
) -> None:
    yarn_args = get_yarn_args(production=production)
    if prefer_offline:
        yarn_args.append("--prefer-offline")
    sha1sum = generate_sha1sum_node_modules(production=production)
    target_path = os.path.join(NODE_MODULES_CACHE_PATH, sha1sum)
    cached_node_modules = os.path.join(target_path, 'node_modules')
    success_stamp = os.path.join(target_path, '.success-stamp')
    # Check if a cached version already exists
    if not os.path.exists(success_stamp):
        do_yarn_install(target_path,
                        yarn_args,
                        success_stamp)

    print("Using cached node modules from %s" % (cached_node_modules,))
    if os.path.islink('node_modules'):
        os.remove('node_modules')
    elif os.path.isdir('node_modules'):
        shutil.rmtree('node_modules')
    os.symlink(cached_node_modules, 'node_modules')