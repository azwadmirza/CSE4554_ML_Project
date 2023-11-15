def parse(root, describe_command=DEFAULT_DESCRIBE, pre_parse=warn_on_shallow):
    """
    :param pre_parse: experimental pre_parse action, may change at any time
    """
    if not has_command("git"):
        return

    wd = GitWorkdir.from_potential_worktree(root)
    if wd is None:
        return
    if pre_parse:
        pre_parse(wd)

    out, err, ret = wd.do_ex(describe_command)
    if ret:
        # If 'git describe' failed, try to get the information otherwise.
        rev_node = wd.node()
        dirty = wd.is_dirty()

        if rev_node is None:
            return meta("0.0", distance=0, dirty=dirty)

        return meta(
            "0.0",
            distance=wd.count_all_nodes(),
            node="g" + rev_node,
            dirty=dirty,
            branch=wd.get_branch(),
        )

    # 'out' looks e.g. like 'v1.5.0-0-g4060507' or
    # 'v1.15.1rc1-37-g9bd1298-dirty'.
    if out.endswith("-dirty"):
        dirty = True
        out = out[:-6]
    else:
        dirty = False

    tag, number, node = out.rsplit("-", 2)
    number = int(number)
    branch = wd.get_branch()
    if number:
        return meta(tag, distance=number, node=node, dirty=dirty, branch=branch)
    else:
        return meta(tag, node=node, dirty=dirty, branch=branch)