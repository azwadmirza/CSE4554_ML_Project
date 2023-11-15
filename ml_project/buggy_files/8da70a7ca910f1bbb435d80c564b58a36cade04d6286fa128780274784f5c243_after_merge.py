    def _mod_init(self, low):
        '''
        Check the module initialization function, if this is the first run
        of a state package that has a mod_init function, then execute the
        mod_init function in the state module.
        '''
        # ensure that the module is loaded
        try:
            self.states['{0}.{1}'.format(low['state'], low['fun'])]  # pylint: disable=W0106
        except KeyError:
            return
        minit = '{0}.mod_init'.format(low['state'])
        if low['state'] not in self.mod_init:
            if minit in self.states._dict:
                mret = self.states[minit](low)
                if not mret:
                    return
                self.mod_init.add(low['state'])