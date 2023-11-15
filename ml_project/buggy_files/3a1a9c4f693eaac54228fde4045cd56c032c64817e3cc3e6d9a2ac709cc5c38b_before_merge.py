def resolveConflicts(actions):
    """Resolve conflicting actions

    Given an actions list, identify and try to resolve conflicting actions.
    Actions conflict if they have the same non-None discriminator.
    Conflicting actions can be resolved if the include path of one of
    the actions is a prefix of the includepaths of the other
    conflicting actions and is unequal to the include paths in the
    other conflicting actions.
    """

    def orderandpos(v):
        n, v = v
        if not isinstance(v, dict):
            # old-style tuple action
            v = expand_action(*v)
        return (v['order'] or 0, n)

    sactions = sorted(enumerate(actions), key=orderandpos)

    def orderonly(v):
        n, v = v
        if not isinstance(v, dict):
            # old-style tuple action
            v = expand_action(*v)
        return v['order'] or 0

    for order, actiongroup in itertools.groupby(sactions, orderonly):
        # "order" is an integer grouping. Actions in a lower order will be
        # executed before actions in a higher order.  All of the actions in
        # one grouping will be executed (its callable, if any will be called)
        # before any of the actions in the next.
        
        unique = {}
        output = []

        for i, action in actiongroup:
            # Within an order, actions are executed sequentially based on
            # original action ordering ("i").

            if not isinstance(action, dict):
                # old-style tuple action
                action = expand_action(*action)

            # "ainfo" is a tuple of (order, i, action) where "order" is a
            # user-supplied grouping, "i" is an integer expressing the relative
            # position of this action in the action list being resolved, and
            # "action" is an action dictionary.  The purpose of an ainfo is to
            # associate an "order" and an "i" with a particular action; "order"
            # and "i" exist for sorting purposes after conflict resolution.
            ainfo = (order, i, action)

            discriminator = undefer(action['discriminator'])
            action['discriminator'] = discriminator

            if discriminator is None:
                # The discriminator is None, so this action can never conflict.
                # We can add it directly to the result.
                output.append(ainfo)
                continue

            L = unique.setdefault(discriminator, [])
            L.append(ainfo)

        # Check for conflicts
        conflicts = {}

        for discriminator, ainfos in unique.items():
            # We use (includepath, order, i) as a sort key because we need to
            # sort the actions by the paths so that the shortest path with a
            # given prefix comes first.  The "first" action is the one with the
            # shortest include path.  We break sorting ties using "order", then
            # "i".
            def bypath(ainfo):
                path, order, i = ainfo[2]['includepath'], ainfo[0], ainfo[1]
                return path, order, i

            ainfos.sort(key=bypath)
            ainfo, rest = ainfos[0], ainfos[1:]
            output.append(ainfo)
            _, _, action = ainfo
            basepath, baseinfo, discriminator = (
                action['includepath'],
                action['info'],
                action['discriminator'],
                )

            for _, _, action in rest:
                includepath = action['includepath']
                # Test whether path is a prefix of opath
                if (includepath[:len(basepath)] != basepath or  # not a prefix
                        includepath == basepath):
                    L = conflicts.setdefault(discriminator, [baseinfo])
                    L.append(action['info'])

        if conflicts:
            raise ConfigurationConflictError(conflicts)

        # sort conflict-resolved actions by (order, i) and yield them one
        # by one
        for a in [x[2] for x in sorted(output, key=operator.itemgetter(0, 1))]:
            yield a