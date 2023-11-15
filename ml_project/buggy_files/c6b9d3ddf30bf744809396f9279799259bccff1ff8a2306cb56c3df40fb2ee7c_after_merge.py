def fetch_index(channel_urls, use_cache=False, unknown=False, index=None):
    log.debug('channel_urls=' + repr(channel_urls))
    # pool = ThreadPool(5)
    if index is None:
        index = {}
    stdoutlog.info("Fetching package metadata ...")
    if not isinstance(channel_urls, dict):
        channel_urls = prioritize_channels(channel_urls)
    for url in iterkeys(channel_urls):
        if allowed_channels and url not in allowed_channels:
            sys.exit("""
Error: URL '%s' not in allowed channels.

Allowed channels are:
  - %s
""" % (url, '\n  - '.join(allowed_channels)))

    try:
        import concurrent.futures
        executor = concurrent.futures.ThreadPoolExecutor(10)
    except (ImportError, RuntimeError):
        # concurrent.futures is only available in Python >= 3.2 or if futures is installed
        # RuntimeError is thrown if number of threads are limited by OS
        session = CondaSession()
        repodatas = [(url, fetch_repodata(url, use_cache=use_cache, session=session))
                     for url in iterkeys(channel_urls)]
    else:
        try:
            urls = tuple(channel_urls)
            futures = tuple(executor.submit(fetch_repodata, url, use_cache=use_cache,
                                            session=CondaSession()) for url in urls)
            repodatas = [(u, f.result()) for u, f in zip(urls, futures)]
        finally:
            executor.shutdown(wait=True)

    for channel, repodata in repodatas:
        if repodata is None:
            continue
        new_index = repodata['packages']
        url_s, priority = channel_urls[channel]
        channel = channel.rstrip('/')
        for fn, info in iteritems(new_index):
            info['fn'] = fn
            info['schannel'] = url_s
            info['channel'] = channel
            info['priority'] = priority
            info['url'] = channel + '/' + fn
            key = url_s + '::' + fn if url_s != 'defaults' else fn
            index[key] = info

    stdoutlog.info('\n')
    if unknown:
        add_unknown(index, channel_urls)
    if add_pip_as_python_dependency:
        add_pip_dependency(index)
    return index