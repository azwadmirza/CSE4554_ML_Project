def explicit(specs, prefix, verbose=False, force_extract=True, index_args=None, index=None):
    actions = defaultdict(list)
    actions['PREFIX'] = prefix

    fetch_specs = []
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

        fetch_specs.append(MatchSpec(url, md5=md5sum) if md5sum else MatchSpec(url))

    pfe = ProgressiveFetchExtract(fetch_specs)
    pfe.execute()

    # now make an UnlinkLinkTransaction with the PackageCacheRecords as inputs
    # need to add package name to fetch_specs so that history parsing keeps track of them correctly
    specs_pcrecs = tuple([spec, next(PackageCacheData.query_all(spec), None)]
                         for spec in fetch_specs)
    assert not any(spec_pcrec[1] is None for spec_pcrec in specs_pcrecs)

    precs_to_remove = []
    prefix_data = PrefixData(prefix)
    for q, (spec, pcrec) in enumerate(specs_pcrecs):
        new_spec = MatchSpec(spec, name=pcrec.name)
        specs_pcrecs[q][0] = new_spec

        prec = prefix_data.get(pcrec.name, None)
        if prec:
            precs_to_remove.append(prec)

    stp = PrefixSetup(prefix, precs_to_remove, tuple(sp[1] for sp in specs_pcrecs),
                      (), tuple(sp[0] for sp in specs_pcrecs))

    txn = UnlinkLinkTransaction(stp)
    txn.execute()