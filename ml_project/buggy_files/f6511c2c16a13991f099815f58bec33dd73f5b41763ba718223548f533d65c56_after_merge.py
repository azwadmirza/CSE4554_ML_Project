def print_explicit(prefix, add_md5=False):
    if not isdir(prefix):
        error_and_exit("Error: environment does not exist: %s" % prefix)
    print_export_header()
    print("@EXPLICIT")
    for meta in sorted(linked_data(prefix).values(), key=lambda x: x['name']):
        url = meta.get('url')
        if not url or url.startswith('<unknown>'):
            print('# no URL for: %s' % meta['fn'])
            continue
        md5 = meta.get('md5')
        print(url + ('#%s' % md5 if add_md5 and md5 else ''))