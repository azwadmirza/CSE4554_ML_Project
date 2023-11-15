def explicit(specs, prefix, verbose=False, force_extract=True, index_args=None, index=None):
    actions = defaultdict(list)
    actions['PREFIX'] = prefix

    fetch_recs = {}
    for spec in specs:
        if spec == '@EXPLICIT':
            continue

        if not is_url(spec):
            spec = unquote(path_to_url(expand(spec)))

        # parse URL
        m = url_pat.match(spec)
        if m is None:
            raise ParseError('Could not parse explicit URL: %s' % spec)
        url_p, fn, md5sum = m.group('url_p'), m.group('fn'), m.group('md5')
        url = join_url(url_p, fn)
        # url_p is everything but the tarball_basename and the md5sum

        # If the path points to a file in the package cache, we need to use
        # the dist name that corresponds to that package. The MD5 may not
        # match, but we will let PFE below worry about that
        dist = None
        if url.startswith('file:/'):
            path = win_path_ok(url_to_path(url))
            if dirname(path) in context.pkgs_dirs:
                if not exists(path):
                    raise FileNotFoundError(path)
                pc_entry = PackageCache.tarball_file_in_cache(path)
                dist = pc_entry.dist
                url = dist.to_url() or pc_entry.get_urls_txt_value()
                md5sum = md5sum or pc_entry.md5sum
        dist = dist or Dist(url)
        fetch_recs[dist] = {'md5': md5sum, 'url': url}

    # perform any necessary fetches and extractions
    if verbose:
        from .console import setup_verbose_handlers
        setup_verbose_handlers()
    link_dists = tuple(iterkeys(fetch_recs))
    pfe = ProgressiveFetchExtract(fetch_recs, link_dists)
    pfe.execute()

    # dists could have been updated with more accurate urls
    # TODO: I'm stuck here

    # Now get the index---but the only index we need is the package cache
    index = {}
    _supplement_index_with_cache(index, ())

    # unlink any installed packages with same package name
    link_names = {index[d]['name'] for d in link_dists}
    actions[UNLINK].extend(d for d, r in iteritems(linked_data(prefix))
                           if r['name'] in link_names)

    # need to get the install order right, especially to install python in the prefix
    #  before python noarch packages
    r = Resolve(index)
    actions[LINK].extend(link_dists)
    actions[LINK] = r.dependency_sort({r.package_name(dist): dist for dist in actions[LINK]})
    actions['ACTION'] = 'EXPLICIT'

    execute_actions(actions, index, verbose=verbose)
    return actions