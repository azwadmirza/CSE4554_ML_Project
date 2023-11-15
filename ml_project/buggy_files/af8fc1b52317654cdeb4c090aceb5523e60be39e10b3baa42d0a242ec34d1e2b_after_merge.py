def explicit(specs, prefix, verbose=False, force_extract=True, fetch_args=None, index=None):
    actions = defaultdict(list)
    actions['PREFIX'] = prefix
    actions['op_order'] = RM_FETCHED, FETCH, RM_EXTRACTED, EXTRACT, UNLINK, LINK
    linked = {name_dist(dist): dist for dist in install_linked(prefix)}
    fetch_args = fetch_args or {}
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

        # See if the URL refers to a package in our cache
        prefix = pkg_path = dir_path = None
        if url.startswith('file://'):
            prefix = cached_url(url)

        # If not, determine the channel name from the URL
        if prefix is None:
            channel, schannel = url_channel(url)
            prefix = '' if schannel == 'defaults' else schannel + '::'
        fn = prefix + fn
        dist = fn[:-8]
        is_file = schannel.startswith('file:') and schannel.endswith('/')
        # Add explicit file to index so we'll see it later
        if is_file:
            index[fn] = {'fn': dist2filename(fn), 'url': url, 'md5': None}

        pkg_path = is_fetched(dist)
        dir_path = is_extracted(dist)

        # Don't re-fetch unless there is an MD5 mismatch
        # Also remove explicit tarballs from cache
        if pkg_path and (is_file or md5 and md5_file(pkg_path) != md5):
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
                if not is_file:
                    if fn not in index or index[fn].get('not_fetched'):
                        channels[url_p + '/'] = (schannel, 0)
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
        index.update(fetch_index(channels, **fetch_args))

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