def create_meta(prefix, dist, info_dir, extra_info):
    """
    Create the conda metadata, in a given prefix, for a given package.
    """
    # read info/index.json first
    with open(join(info_dir, 'index.json')) as fi:
        meta = json.load(fi)
    # add extra info, add to our intenral cache
    meta.update(extra_info)
    if not meta.get('url'):
        meta['url'] = read_url(dist)
    # write into <env>/conda-meta/<dist>.json
    meta_dir = join(prefix, 'conda-meta')
    if not isdir(meta_dir):
        os.makedirs(meta_dir)
    with open(join(meta_dir, dist2filename(dist, '.json')), 'w') as fo:
        json.dump(meta, fo, indent=2, sort_keys=True)
    if prefix in linked_data_:
        load_linked_data(prefix, dist, meta)