def print_explicit(prefix, add_md5=False):
    from ..base.constants import UNKNOWN_CHANNEL
    from ..base.context import context
    from ..core.linked_data import linked_data
    if not isdir(prefix):
        from ..exceptions import CondaEnvironmentNotFoundError
        raise CondaEnvironmentNotFoundError(prefix)
    print_export_header(context.subdir)
    print("@EXPLICIT")
    for meta in sorted(linked_data(prefix).values(), key=lambda x: x['name']):
        url = meta.get('url')
        if not url or url.startswith(UNKNOWN_CHANNEL):
            print('# no URL for: %s' % meta['fn'])
            continue
        md5 = meta.get('md5')
        print(url + ('#%s' % md5 if add_md5 and md5 else ''))