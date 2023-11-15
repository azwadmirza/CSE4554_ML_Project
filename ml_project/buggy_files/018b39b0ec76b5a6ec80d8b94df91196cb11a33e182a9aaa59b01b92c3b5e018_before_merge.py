def parse(root):
    l = do('hg id -i -t', root).split()
    node = l.pop(0)
    tags = tags_to_versions(l)
    # filter tip in degraded mode on old setuptools
    tags = [x for x in tags if x != 'tip']
    dirty = node[-1] == '+'
    if tags:
        return meta(tags[0], dirty=dirty)

    if node.strip('+') == '0'*12:
        trace('initial node', root)
        return meta('0.0', dirty=dirty)

    cmd = 'hg parents --template "{latesttag} {latesttagdistance}"'
    out = do(cmd, root)
    try:
        tag, dist = out.split()
        if tag == 'null':
            tag = '0.0'
            dist = int(dist) + 1
        return _hg_tagdist_normalize_tagcommit(root, tag, dist, node)
    except ValueError:
        pass  # unpacking failed, old hg