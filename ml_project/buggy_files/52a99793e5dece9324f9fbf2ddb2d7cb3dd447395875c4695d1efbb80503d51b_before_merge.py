    def execute_actions(self, clear=True, introspector=None):
        """Execute the configuration actions

        This calls the action callables after resolving conflicts

        For example:

        >>> output = []
        >>> def f(*a, **k):
        ...    output.append(('f', a, k))
        >>> context = ActionState()
        >>> context.actions = [
        ...   (1, f, (1,)),
        ...   (1, f, (11,), {}, ('x', )),
        ...   (2, f, (2,)),
        ...   ]
        >>> context.execute_actions()
        >>> output
        [('f', (1,), {}), ('f', (2,), {})]

        If the action raises an error, we convert it to a
        ConfigurationExecutionError.

        >>> output = []
        >>> def bad():
        ...    bad.xxx
        >>> context.actions = [
        ...   (1, f, (1,)),
        ...   (1, f, (11,), {}, ('x', )),
        ...   (2, f, (2,)),
        ...   (3, bad, (), {}, (), 'oops')
        ...   ]
        >>> try:
        ...    v = context.execute_actions()
        ... except ConfigurationExecutionError, v:
        ...    pass
        >>> print(v)
        exceptions.AttributeError: 'function' object has no attribute 'xxx'
          in:
          oops

        Note that actions executed before the error still have an effect:

        >>> output
        [('f', (1,), {}), ('f', (2,), {})]

        The execution is re-entrant such that actions may be added by other
        actions with the one caveat that the order of any added actions must
        be equal to or larger than the current action.

        >>> output = []
        >>> def f(*a, **k):
        ...   output.append(('f', a, k))
        ...   context.actions.append((3, g, (8,), {}))
        >>> def g(*a, **k):
        ...    output.append(('g', a, k))
        >>> context.actions = [
        ...   (1, f, (1,)),
        ...   ]
        >>> context.execute_actions()
        >>> output
        [('f', (1,), {}), ('g', (8,), {})]

        """
        try:
            all_actions = []
            executed_actions = []
            pending_actions = iter([])

            # resolve the new action list against what we have already
            # executed -- if a new action appears intertwined in the list
            # of already-executed actions then someone wrote a broken
            # re-entrant action because it scheduled the action *after* it
            # should have been executed (as defined by the action order)
            def resume(actions):
                for a, b in zip_longest(actions, executed_actions):
                    if b is None and a is not None:
                        # common case is that we are executing every action
                        yield a
                    elif b is not None and a != b:
                        raise ConfigurationError(
                            'During execution a re-entrant action was added '
                            'that modified the planned execution order in a '
                            'way that is incompatible with what has already '
                            'been executed.')
                    else:
                        # resolved action is in the same location as before,
                        # so we are in good shape, but the action is already
                        # executed so we skip it
                        assert b is not None and a == b

            while True:
                # We clear the actions list prior to execution so if there
                # are some new actions then we add them to the mix and resolve
                # conflicts again. This orders the new actions as well as
                # ensures that the previously executed actions have no new
                # conflicts.
                if self.actions:
                    # Only resolve the new actions against executed_actions
                    # and pending_actions instead of everything to avoid
                    # redundant checks.
                    # Assume ``actions = resolveConflicts([A, B, C])`` which
                    # after conflict checks, resulted in ``actions == [A]``
                    # then we know action A won out or a conflict would have
                    # been raised. Thus, when action D is added later, we only
                    # need to check the new action against A.
                    # ``actions = resolveConflicts([A, D]) should drop the
                    # number of redundant checks down from O(n^2) closer to
                    # O(n lg n).
                    all_actions.extend(self.actions)
                    pending_actions = resume(resolveConflicts(
                        executed_actions +
                        list(pending_actions) +
                        self.actions
                    ))
                    self.actions = []

                action = next(pending_actions, None)
                if action is None:
                    # we are done!
                    break

                callable = action['callable']
                args = action['args']
                kw = action['kw']
                info = action['info']
                # we use "get" below in case an action was added via a ZCML
                # directive that did not know about introspectables
                introspectables = action.get('introspectables', ())

                try:
                    if callable is not None:
                        callable(*args, **kw)
                except (KeyboardInterrupt, SystemExit): # pragma: no cover
                    raise
                except:
                    t, v, tb = sys.exc_info()
                    try:
                        reraise(ConfigurationExecutionError,
                                ConfigurationExecutionError(t, v, info),
                                tb)
                    finally:
                        del t, v, tb

                if introspector is not None:
                    for introspectable in introspectables:
                        introspectable.register(introspector, info)

                executed_actions.append(action)

        finally:
            if clear:
                del self.actions[:]
            else:
                self.actions = all_actions