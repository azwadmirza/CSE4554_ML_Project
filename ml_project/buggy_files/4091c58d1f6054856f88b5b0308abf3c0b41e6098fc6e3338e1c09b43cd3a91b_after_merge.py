def _qemu_image_info(path):
    '''
    Detect information for the image at path
    '''
    ret = {}
    out = __salt__['cmd.run']('qemu-img info {0}'.format(path))

    match_map = {'size': r'virtual size: \w+ \((\d+) byte[s]?\)',
                 'format': r'file format: (\w+)'}

    for info, search in match_map.items():
        try:
            ret[info] = re.search(search, out).group(1)
        except AttributeError:
            continue
    return ret