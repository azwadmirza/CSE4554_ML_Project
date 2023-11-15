def resolveConflicts(actions, state=None):
    """Resolve conflicting actions

    Given an actions list, identify and try to resolve conflicting actions.
    Actions conflict if they have the same non-None discriminator.

    Conflicting actions can be resolved if the include path of one of
    the actions is a prefix of the includepaths of the other
    conflicting actions and is unequal to the include paths in the
    other conflicting actions.

    Actions are resolved on a per-order basis because some discriminators
    cannot be computed until earlier actions have executed. An action in an
    earlier order may execute successfully only to find out later that it was
    overridden by another action with a smaller include path. This will result
    in a conflict as there is no way to revert the original action.

    ``state`` may be an instance of ``ConflictResolverState`` that
    can be used to resume execution and resolve the new actions against the
    list of executed actions from a previous call.

    """
    if state is None:
        state = ConflictResolverState()

    # pick up where we left off last time, but track the new actions as well
    state.remaining_actions.extend(normalize_actions(actions))
    actions = state.remaining_actions

    def orderandpos(v):
        n, v = v
        return (v['order'] or 0, n)

    def orderonly(v):
        n, v = v
        return v['order'] or 0

    sactions = sorted(enumerate(actions, start=state.start), key=orderandpos)
    for order, actiongroup in itertools.groupby(sactions, orderonly):
        # "order" is an integer grouping. Actions in a lower order will be
        # executed before actions in a higher order.  All of the actions in
        # one grouping will be executed (its callable, if any will be called)
        # before any of the actions in the next.
        output = []
        unique = {}

        # error out if we went backward in order
        if state.min_order is not None and order < state.min_order:
            r = ['Actions were added to order={0} after execution had moved '
                 'on to order={1}. Conflicting actions: '
                 .format(order, state.min_order)]
            for i, action in actiongroup:
                for line in str(action['info']).rstrip().split('\n'):
                    r.append("  " + line)
            raise ConfigurationError('\n'.join(r))

        for i, action in actiongroup:
            # Within an order, actions are executed sequentially based on
            # original action ordering ("i").

            # "ainfo" is a tuple of (i, action) where "i" is an integer
            # expressing the relative position of this action in the action
            # list being resolved, and "action" is an action dictionary.  The
            # purpose of an ainfo is to associate an "i" with a particular
            # action; "i" exists for sorting after conflict resolution.
            ainfo = (i, action)

            # wait to defer discriminators until we are on their order because
            # the discriminator may depend on state from a previous order
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
            # We use (includepath, i) as a sort key because we need to
            # sort the actions by the paths so that the shortest path with a
            # given prefix comes first.  The "first" action is the one with the
            # shortest include path.  We break sorting ties using "i".
            def bypath(ainfo):
                path, i = ainfo[1]['includepath'], ainfo[0]
                return path, order, i

            ainfos.sort(key=bypath)
            ainfo, rest = ainfos[0], ainfos[1:]
            _, action = ainfo

            # ensure this new action does not conflict with a previously
            # resolved action from an earlier order / invocation
            prev_ainfo = state.resolved_ainfos.get(discriminator)
            if prev_ainfo is not None:
                _, paction = prev_ainfo
                basepath, baseinfo = paction['includepath'], paction['info']
                includepath = action['includepath']
                # if the new action conflicts with the resolved action then
                # note the conflict, otherwise drop the action as it's
                # effectively overriden by the previous action
                if (includepath[:len(basepath)] != basepath or
                        includepath == basepath):
                    L = conflicts.setdefault(discriminator, [baseinfo])
                    L.append(action['info'])

            else:
                output.append(ainfo)

            basepath, baseinfo = action['includepath'], action['info']
            for _, action in rest:
                includepath = action['includepath']
                # Test whether path is a prefix of opath
                if (includepath[:len(basepath)] != basepath or  # not a prefix
                        includepath == basepath):
                    L = conflicts.setdefault(discriminator, [baseinfo])
                    L.append(action['info'])

        if conflicts:
            raise ConfigurationConflictError(conflicts)

        # sort resolved actions by "i" and yield them one by one
        for i, action in sorted(output, key=operator.itemgetter(0)):
            # do not memoize the order until we resolve an action inside it
            state.min_order = action['order']
            state.start = i + 1
            state.remaining_actions.remove(action)
            state.resolved_ainfos[action['discriminator']] = (i, action)
            yield action