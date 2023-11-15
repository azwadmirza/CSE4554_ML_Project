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
    if 'fn' not in rec:
        rec['fn'] = url.rsplit('/', 1)[-1] if url else dname + '.tar.bz2'
    if not url and 'channel' in rec:
        url = rec['url'] = rec['channel'] + rec['fn']
    if rec['fn'][:-8] != dname:
        log.debug('Ignoring invalid package metadata file: %s' % meta_file)
        return None
    channel, schannel = url_channel(url)
    rec['channel'] = channel
    rec['schannel'] = schannel
    rec['link'] = rec.get('link') or True
    cprefix = '' if schannel == 'defaults' else schannel + '::'
    linked_data_[prefix][str(cprefix + dname)] = rec
    return rec