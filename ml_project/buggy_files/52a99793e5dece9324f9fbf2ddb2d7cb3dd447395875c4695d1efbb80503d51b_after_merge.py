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
            action_iter = iter([])
            conflict_state = ConflictResolverState()

            while True:
                # We clear the actions list prior to execution so if there
                # are some new actions then we add them to the mix and resolve
                # conflicts again. This orders the new actions as well as
                # ensures that the previously executed actions have no new
                # conflicts.
                if self.actions:
                    all_actions.extend(self.actions)
                    action_iter = resolveConflicts(
                        self.actions,
                        state=conflict_state,
                    )
                    self.actions = []

                action = next(action_iter, None)
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
                except Exception:
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

            self.actions = all_actions
            return executed_actions

        finally:
            if clear:
                self.actions = []