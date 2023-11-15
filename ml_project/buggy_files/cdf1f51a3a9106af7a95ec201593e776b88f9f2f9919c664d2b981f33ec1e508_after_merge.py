def dist2quad(dist):
    channel, dist = dist2pair(dist)
    parts = dist.rsplit('-', 2) + ['', '']
    return (parts[0], parts[1], parts[2], channel)