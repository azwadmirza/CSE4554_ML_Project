def explicit(specs, prefix, verbose=False, force_extract=True, index_args=None, index=None):
    actions = defaultdict(list)
    actions['PREFIX'] = prefix
    actions['op_order'] = RM_FETCHED, FETCH, RM_EXTRACTED, EXTRACT, UNLINK, LINK, SYMLINK_CONDA
    linked = {name_dist(dist): dist for dist in install_linked(prefix)}
    index_args = index_args or {}
    index = index or {}
    verifies = []
    channels = {}
    for spec in specs:
        if spec == '@EXPLICIT':
            continue

        # Format: (url|path)(:#md5)?
        m = url_pat.match(spec)
        if m is None:
            sys.exit('Could not parse explicit URL: %s' % spec)
        url_p, fn, md5 = m.group('url_p'), m.group('fn'), m.group('md5')
        if not is_url(url_p):
            if url_p is None:
                url_p = curdir
            elif not isdir(url_p):
                sys.exit('Error: file not found: %s' % join(url_p, fn))
            url_p = utils_url_path(url_p).rstrip('/')
        url = "{0}/{1}".format(url_p, fn)

        # is_local: if the tarball is stored locally (file://)
        # is_cache: if the tarball is sitting in our cache
        is_local = url.startswith('file://')
        prefix = cached_url(url) if is_local else None
        is_cache = prefix is not None
        if is_cache:
            # Channel information from the cache
            schannel = 'defaults' if prefix == '' else prefix[:-2]
        else:
            # Channel information from the URL
            channel, schannel = url_channel(url)
            prefix = '' if schannel == 'defaults' else schannel + '::'

        fn = prefix + fn
        dist = fn[:-8]
        # Add explicit file to index so we'll be sure to see it later
        if is_local:
            index[fn] = {'fn': dist2filename(fn), 'url': url, 'md5': md5}
            verifies.append((fn, md5))

        pkg_path = is_fetched(dist)
        dir_path = is_extracted(dist)

        # Don't re-fetch unless there is an MD5 mismatch
        # Also remove explicit tarballs from cache, unless the path *is* to the cache
        if pkg_path and not is_cache and (is_local or md5 and md5_file(pkg_path) != md5):
            # This removes any extracted copies as well
            actions[RM_FETCHED].append(dist)
            pkg_path = dir_path = None

        # Don't re-extract unless forced, or if we can't check the md5
        if dir_path and (force_extract or md5 and not pkg_path):
            actions[RM_EXTRACTED].append(dist)
            dir_path = None

        if not dir_path:
            if not pkg_path:
                _, conflict = find_new_location(dist)
                if conflict:
                    actions[RM_FETCHED].append(conflict)
                if not is_local:
                    if fn not in index or index[fn].get('not_fetched'):
                        channels.add(channel)
                    verifies.append((dist + '.tar.bz2', md5))
                actions[FETCH].append(dist)
            actions[EXTRACT].append(dist)

        # unlink any installed package with that name
        name = name_dist(dist)
        if name in linked:
            actions[UNLINK].append(linked[name])
        actions[LINK].append(dist)

    # Pull the repodata for channels we are using
    if channels:
        index_args = index_args or {}
        index_args = index_args.copy()
        index_args['prepend'] = False
        index_args['channel_urls'] = channels
        index.update(get_index(**index_args))

    # Finish the MD5 verification
    for fn, md5 in verifies:
        info = index.get(fn)
        if info is None:
            sys.exit("Error: no package '%s' in index" % fn)
        if md5 and 'md5' not in info:
            sys.stderr.write('Warning: cannot lookup MD5 of: %s' % fn)
        if md5 and info['md5'] != md5:
            sys.exit(
                'MD5 mismatch for: %s\n   spec: %s\n   repo: %s'
                % (fn, md5, info['md5']))

    execute_actions(actions, index=index, verbose=verbose)
    return actions