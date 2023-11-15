def list_packages(prefix, installed, regex=None, format='human',
                  show_channel_urls=show_channel_urls):
    res = 1

    result = []
    for dist in get_packages(installed, regex):
        res = 0
        if format == 'canonical':
            result.append(dist)
            continue
        if format == 'export':
            result.append('='.join(dist2quad(dist)[:3]))
            continue

        try:
            # Returns None if no meta-file found (e.g. pip install)
            info = is_linked(prefix, dist)
            features = set(info.get('features', '').split())
            disp = '%(name)-25s %(version)-15s %(build)15s' % info
            disp += '  %s' % disp_features(features)
            schannel = info.get('schannel')
            if show_channel_urls or show_channel_urls is None and schannel != 'defaults':
                disp += '  %s' % schannel
            result.append(disp)
        except (AttributeError, IOError, KeyError, ValueError) as e:
            log.debug(str(e))
            result.append('%-25s %-15s %15s' % dist2quad(dist)[:3])

    return res, result