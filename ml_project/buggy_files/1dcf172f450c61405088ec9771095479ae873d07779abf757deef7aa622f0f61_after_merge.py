def add_cached_package(pdir, url, overwrite=False, urlstxt=False):
    """
    Adds a new package to the cache. The URL is used to determine the
    package filename and channel, and the directory pdir is scanned for
    both a compressed and an extracted version of that package. If
    urlstxt=True, this URL will be appended to the urls.txt file in the
    cache, so that subsequent runs will correctly identify the package.
    """
    package_cache()
    if '/' in url:
        dist = url.rsplit('/', 1)[-1]
    else:
        dist = url
        url = None
    if dist.endswith('.tar.bz2'):
        fname = dist
        dist = dist[:-8]
    else:
        fname = dist + '.tar.bz2'
    xpkg = join(pdir, fname)
    if not overwrite and xpkg in fname_table_:
        return
    if not isfile(xpkg):
        xpkg = None
    xdir = join(pdir, dist)
    if not (isdir(xdir) and
            isfile(join(xdir, 'info', 'files')) and
            isfile(join(xdir, 'info', 'index.json'))):
        xdir = None
    if not (xpkg or xdir):
        return
    if url:
        url = remove_binstar_tokens(url)
    _, schannel = url_channel(url)
    prefix = '' if schannel == 'defaults' else schannel + '::'
    xkey = xpkg or (xdir + '.tar.bz2')
    fname_table_[xkey] = fname_table_[url_path(xkey)] = prefix
    fkey = prefix + dist
    rec = package_cache_.get(fkey)
    if rec is None:
        rec = package_cache_[fkey] = dict(files=[], dirs=[], urls=[])
    if url and url not in rec['urls']:
        rec['urls'].append(url)
    if xpkg and xpkg not in rec['files']:
        rec['files'].append(xpkg)
    if xdir and xdir not in rec['dirs']:
        rec['dirs'].append(xdir)
    if urlstxt:
        try:
            with open(join(pdir, 'urls.txt'), 'a') as fa:
                fa.write('%s\n' % url)
        except IOError:
            pass