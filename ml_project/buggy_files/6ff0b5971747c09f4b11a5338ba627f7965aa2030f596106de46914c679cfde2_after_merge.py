def add_unknown(index, priorities):
    priorities = {p[0]: p[1] for p in itervalues(priorities)}
    maxp = max(itervalues(priorities)) + 1 if priorities else 1
    for dist, info in iteritems(package_cache()):
        schannel, dname = dist2pair(dist)
        fname = dname + '.tar.bz2'
        fkey = dist + '.tar.bz2'
        if fkey in index or not info['dirs']:
            continue
        try:
            with open(join(info['dirs'][0], 'info', 'index.json')) as fi:
                meta = json.load(fi)
        except IOError:
            continue
        if info['urls']:
            url = info['urls'][0]
        elif meta.get('url'):
            url = meta['url']
        elif meta.get('channel'):
            url = meta['channel'].rstrip('/') + '/' + fname
        else:
            url = '<unknown>/' + fname
        if url.rsplit('/', 1)[-1] != fname:
            continue
        channel, schannel2 = url_channel(url)
        if schannel2 != schannel:
            continue
        priority = priorities.get(schannel, maxp)
        if 'link' in meta:
            del meta['link']
        meta.update({'fn': fname, 'url': url, 'channel': channel,
                     'schannel': schannel, 'priority': priority})
        meta.setdefault('depends', [])
        log.debug("adding cached pkg to index: %s" % fkey)
        index[fkey] = meta