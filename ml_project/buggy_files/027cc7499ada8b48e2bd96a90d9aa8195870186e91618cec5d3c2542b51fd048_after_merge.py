    def restore(self, name='default', filename=None):
        '''
        restore(name='default', filename=None)

        Retore the state of the network and all included objects.

        Parameters
        ----------
        name : str, optional
            The name of the snapshot to restore, if not specified uses
            ``'default'``.
        filename : str, optional
            The name of the file from where the state should be restored. If
            not specified, it is expected that the state exist in memory
            (i.e. `Network.store` was previously called without the ``filename``
            argument).
        '''
        if filename is None:
            state = self._stored_state[name]
        else:
            with open(filename, 'rb') as f:
                state = pickle.load(f)[name]
        self.t_ = state['0_t']
        clocks = set([obj.clock for obj in self.objects])
        restored_objects = set()
        for obj in self.objects:
            if obj.name in state:
                obj._restore_from_full_state(state[obj.name])
                restored_objects.add(obj.name)
            elif hasattr(obj, '_restore_from_full_state'):
                raise KeyError(('Stored state does not have a stored state for '
                                '"%s". Note that the names of all objects have '
                                'to be identical to the names when they were '
                                'stored.') % obj.name)
        for clock in clocks:
            clock._restore_from_full_state(state[clock.name])
        clock_names = {c.name for c in clocks}

        unnused = set(state.keys()) - restored_objects - clock_names - {'0_t'}
        if len(unnused):
            raise KeyError('The stored state contains the state of the '
                           'following objects which were not present in the '
                           'network: %s. Note that the names of all objects '
                           'have to be identical to the names when they were '
                           'stored.' % (', '.join(unnused)))