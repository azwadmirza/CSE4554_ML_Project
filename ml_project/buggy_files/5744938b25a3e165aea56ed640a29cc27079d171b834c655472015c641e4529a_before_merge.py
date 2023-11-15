def load_linked_data(prefix, dist, rec=None):
    schannel, dname = dist2pair(dist)
    meta_file = join(prefix, 'conda-meta', dname + '.json')
    if rec is None:
        try:
            with open(meta_file) as fi:
                rec = json.load(fi)
        except IOError:
            return None
    else:
        linked_data(prefix)
    url = rec.get('url')
    fn = rec.get('fn')
    if not fn:
        fn = rec['fn'] = url.rsplit('/', 1)[-1] if url else dname + '.tar.bz2'
    if fn[:-8] != dname:
        log.debug('Ignoring invalid package metadata file: %s' % meta_file)
        return None
    channel = rec.get('channel')
    if channel:
        channel = channel.rstrip('/')
        if not url or (url.startswith('file:') and channel[0] != '<unknown>'):
            url = rec['url'] = channel + '/' + fn
    channel, schannel = url_channel(url)
    rec['channel'] = channel
    rec['schannel'] = schannel
    rec['link'] = rec.get('link') or True
    cprefix = '' if schannel == 'defaults' else schannel + '::'
    linked_data_[prefix][str(cprefix + dname)] = rec
    return rec