def list_packages(prefix, installed, regex=None, format='human',
                  show_channel_urls=None):
    from .common import disp_features
    from ..base.constants import DEFAULTS_CHANNEL_NAME
    from ..base.context import context
    from ..core.linked_data import is_linked
    res = 0
    result = []
    for dist in get_packages(installed, regex):
        if format == 'canonical':
            result.append(dist)
            continue
        if format == 'export':
            result.append('='.join(dist.quad[:3]))
            continue

        try:
            # Returns None if no meta-file found (e.g. pip install)
            info = is_linked(prefix, dist)
            features = set(info.get('features', '').split())
            disp = '%(name)-25s %(version)-15s %(build)15s' % info
            disp += '  %s' % disp_features(features)
            schannel = info.get('schannel')
            show_channel_urls = show_channel_urls or context.show_channel_urls
            if (show_channel_urls or show_channel_urls is None
                    and schannel != DEFAULTS_CHANNEL_NAME):
                disp += '  %s' % schannel
            result.append(disp)
        except (AttributeError, IOError, KeyError, ValueError) as e:
            log.debug("exception for dist %s:\n%r", dist, e)
            result.append('%-25s %-15s %15s' % tuple(dist.quad[:3]))

    return res, result