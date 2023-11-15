def load_linked_data(prefix, dist, rec=None):
    schannel, dname = dist2pair(dist)
    if rec is None:
        meta_file = join(prefix, 'conda-meta', dname + '.json')
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
    channel, schannel = url_channel(url)
    rec['channel'] = channel
    rec['schannel'] = schannel
    cprefix = '' if schannel == 'defaults' else schannel + '::'
    linked_data_[prefix][str(cprefix + dname)] = rec
    return rec