def print_explicit(prefix, add_md5=False):
    import json

    if not isdir(prefix):
        error_and_exit("Error: environment does not exist: %s" % prefix)
    print_export_header()
    print("@EXPLICIT")

    meta_dir = join(prefix, 'conda-meta')
    for fn in sorted(os.listdir(meta_dir)):
        if not fn.endswith('.json'):
            continue
        with open(join(meta_dir, fn)) as fi:
            meta = json.load(fi)
        url = meta.get('url')

        def format_url():
            return '%s%s-%s-%s.tar.bz2' % (meta['channel'], meta['name'],
                                           meta['version'], meta['build'])
        # two cases in which we want to try to format the url:
        # 1. There is no url key in the metadata
        # 2. The url key in the metadata is referencing a file on the local
        #    machine
        if not url:
            try:
                url = format_url()
            except KeyError:
                # Declare failure :-(
                print('# no URL for: %s' % fn[:-5])
                continue
        if url.startswith('file'):
            try:
                url = format_url()
            except KeyError:
                # declare failure and allow the url to be the file from which it was
                # originally installed
                continue
        md5 = meta.get('md5')
        print(url + ('#%s' % md5 if add_md5 and md5 else ''))