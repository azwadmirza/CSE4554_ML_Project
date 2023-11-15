def parse(root, describe_command=DEFAULT_DESCRIBE):
    wd = GitWorkdir(root)

    rev_node = wd.node()
    dirty = wd.is_dirty()

    if rev_node is None:
        return meta('0.0', distance=0, dirty=dirty)

    out, err, ret = do_ex(describe_command, root)
    if ret:
        return meta(
            '0.0',
            distance=wd.count_all_nodes(),
            node=rev_node,
            dirty=dirty,
        )

    tag, number, node = out.rsplit('-', 2)
    number = int(number)
    if number:
        return meta(tag, distance=number, node=node, dirty=dirty)
    else:
        return meta(tag, node=node, dirty=dirty)