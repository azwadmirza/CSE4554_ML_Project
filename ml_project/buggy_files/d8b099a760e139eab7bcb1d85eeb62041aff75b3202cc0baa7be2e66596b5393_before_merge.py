def clone_env(prefix1, prefix2, verbose=True, quiet=False, fetch_args=None):
    """
    clone existing prefix1 into new prefix2
    """
    untracked_files = untracked(prefix1)

    # Discard conda and any package that depends on it
    drecs = linked_data(prefix1)
    filter = {}
    found = True
    while found:
        found = False
        for dist, info in iteritems(drecs):
            name = info['name']
            if name in filter:
                continue
            if name == 'conda':
                filter['conda'] = dist
                found = True
                break
            for dep in info.get('depends', []):
                if MatchSpec(dep).name in filter:
                    filter[name] = dist
                    found = True
    if filter:
        if not quiet:
            print('The following packages cannot be cloned out of the root environment:')
            for pkg in itervalues(filter):
                print(' - ' + pkg)
            drecs = {dist: info for dist, info in iteritems(drecs) if info['name'] not in filter}

    # Resolve URLs for packages that do not have URLs
    r = None
    index = {}
    unknowns = [dist for dist, info in iteritems(drecs) if 'url' not in info]
    notfound = []
    if unknowns:
        fetch_args = fetch_args or {}
        index = get_index(**fetch_args)
        r = Resolve(index, sort=True)
        for dist in unknowns:
            name = name_dist(dist)
            fn = dist2filename(dist)
            fkeys = [d for d in r.index.keys() if r.index[d]['fn'] == fn]
            if fkeys:
                del drecs[dist]
                dist = sorted(fkeys, key=r.version_key, reverse=True)[0]
                drecs[dist] = r.index[dist]
            else:
                notfound.append(fn)
    if notfound:
        what = "Package%s " % ('' if len(notfound) == 1 else 's')
        notfound = '\n'.join(' - ' + fn for fn in notfound)
        msg = '%s missing in current %s channels:%s' % (what, subdir, notfound)
        raise RuntimeError(msg)

    # Assemble the URL and channel list
    urls = {}
    resolver = None
    for dist, info in iteritems(drecs):
        fkey = dist + '.tar.bz2'
        if fkey not in index:
            info['not_fetched'] = True
            index[fkey] = info
            r = None
        urls[dist] = info['url']

    if r is None:
        r = Resolve(index)
    dists = r.dependency_sort(urls.keys())
    urls = [urls[d] for d in dists]

    if verbose:
        print('Packages: %d' % len(dists))
        print('Files: %d' % len(untracked_files))

    for f in untracked_files:
        src = join(prefix1, f)
        dst = join(prefix2, f)
        dst_dir = dirname(dst)
        if islink(dst_dir) or isfile(dst_dir):
            os.unlink(dst_dir)
        if not isdir(dst_dir):
            os.makedirs(dst_dir)
        if islink(src):
            os.symlink(os.readlink(src), dst)
            continue

        try:
            with open(src, 'rb') as fi:
                data = fi.read()
        except IOError:
            continue

        try:
            s = data.decode('utf-8')
            s = s.replace(prefix1, prefix2)
            data = s.encode('utf-8')
        except UnicodeDecodeError:  # data is binary
            pass

        with open(dst, 'wb') as fo:
            fo.write(data)
        shutil.copystat(src, dst)

    actions = explicit(urls, prefix2, verbose=not quiet, index=index,
                       force_extract=False, fetch_args=fetch_args)
    return actions, untracked_files