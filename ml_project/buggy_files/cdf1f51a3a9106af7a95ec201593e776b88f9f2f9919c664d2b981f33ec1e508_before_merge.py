def dist2quad(dist, channel=True):
    dist = str(dist)
    if dist.endswith('.tar.bz2'):
        dist = dist[:-8]
    parts = dist.rsplit('-', 2)
    if len(parts) < 3:
        parts = parts + [''] * (3 - len(parts))
    chan_name, version, build = parts
    if not channel:
        return chan_name, version, build
    parts = chan_name.split('::')
    return (parts[-1], version, build,
            'defaults' if len(parts) < 2 else parts[0])