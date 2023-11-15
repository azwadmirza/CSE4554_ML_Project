def clone_env(prefix1, prefix2, verbose=True, quiet=False, index_args=None):
    """
    clone existing prefix1 into new prefix2
    """
    untracked_files = untracked(prefix1)

    # Discard conda, conda-env and any package that depends on them
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
            if name == "conda-env":
                filter["conda-env"] = dist
                found = True
                break
            for dep in info.combined_depends:
                if MatchSpec(dep).name in filter:
                    filter[name] = dist
                    found = True

    if filter:
        if not quiet:
            fh = sys.stderr if context.json else sys.stdout
            print('The following packages cannot be cloned out of the root environment:', file=fh)
            for pkg in itervalues(filter):
                print(' - ' + pkg.dist_name, file=fh)
            drecs = {dist: info for dist, info in iteritems(drecs) if info['name'] not in filter}

    # Resolve URLs for packages that do not have URLs
    r = None
    index = {}
    unknowns = [dist for dist, info in iteritems(drecs) if not info.get('url')]
    notfound = []
    if unknowns:
        index_args = index_args or {}
        index = get_index(**index_args)
        r = Resolve(index, sort=True)
        for dist in unknowns:
            name = dist.dist_name
            fn = dist.to_filename()
            fkeys = [d for d in r.index.keys() if r.index[d]['fn'] == fn]
            if fkeys:
                del drecs[dist]
                dist_str = sorted(fkeys, key=r.version_key, reverse=True)[0]
                drecs[Dist(dist_str)] = r.index[dist_str]
            else:
                notfound.append(fn)
    if notfound:
        raise PackagesNotFoundError(notfound)

    # Assemble the URL and channel list
    urls = {}
    for dist, info in iteritems(drecs):
        fkey = dist
        if fkey not in index:
            index[fkey] = PackageRecord.from_objects(info, not_fetched=True)
            r = None
        urls[dist] = info['url']

    if r is None:
        r = Resolve(index)
    dists = r.dependency_sort({d.quad[0]: d for d in urls.keys()})
    urls = [urls[d] for d in dists]

    precs = tuple(index[dist] for dist in dists)
    disallowed = tuple(MatchSpec(s) for s in context.disallowed_packages)
    for prec in precs:
        if any(d.match(prec) for d in disallowed):
            raise DisallowedPackageError(prec)

    if verbose:
        print('Packages: %d' % len(dists))
        print('Files: %d' % len(untracked_files))

    for f in untracked_files:
        src = join(prefix1, f)
        dst = join(prefix2, f)
        dst_dir = dirname(dst)
        if islink(dst_dir) or isfile(dst_dir):
            rm_rf(dst_dir)
        if not isdir(dst_dir):
            os.makedirs(dst_dir)
        if islink(src):
            symlink(readlink(src), dst)
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
                       force_extract=False, index_args=index_args)
    return actions, untracked_files