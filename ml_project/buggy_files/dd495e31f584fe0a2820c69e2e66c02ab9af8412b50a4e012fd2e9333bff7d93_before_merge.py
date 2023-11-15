    def render_pstate(self, sls, saltenv, mods, defaults=None):
        '''
        Collect a single pillar sls file and render it
        '''
        if defaults is None:
            defaults = {}
        err = ''
        errors = []
        fn_ = self.client.get_state(sls, saltenv).get('dest', False)
        if not fn_:
            if sls in self.ignored_pillars.get(saltenv, []):
                log.debug('Skipping ignored and missing SLS \'{0}\' in'
                          ' environment \'{1}\''.format(sls, saltenv))
                return None, mods, errors
            elif self.opts['pillar_roots'].get(saltenv):
                msg = ('Specified SLS \'{0}\' in environment \'{1}\' is not'
                       ' available on the salt master').format(sls, saltenv)
                log.error(msg)
                errors.append(msg)
            else:
                log.debug(
                    'Specified SLS \'%s\' in environment \'%s\' was not '
                    'found. This could be because SLS \'%s\' is in an '
                    'environment other than \'%s\', but \'%s\' is included in '
                    'that environment\'s Pillar top file. It could also be '
                    'due to environment \'%s\' not being defined in '
                    '"pillar_roots"',
                    sls, saltenv, sls, saltenv, saltenv, saltenv
                )
                # return state, mods, errors
                return None, mods, errors
        state = None
        try:
            state = compile_template(fn_,
                                     self.rend,
                                     self.opts['renderer'],
                                     saltenv,
                                     sls,
                                     _pillar_rend=True,
                                     **defaults)
        except Exception as exc:
            msg = 'Rendering SLS \'{0}\' failed, render error:\n{1}'.format(
                sls, exc
            )
            log.critical(msg)
            if self.opts.get('pillar_safe_render_error', True):
                errors.append(
                    'Rendering SLS \'{0}\' failed. Please see master log for '
                    'details.'.format(sls)
                )
            else:
                errors.append(msg)
        mods.add(sls)
        nstate = None
        if state:
            if not isinstance(state, dict):
                msg = 'SLS \'{0}\' does not render to a dictionary'.format(sls)
                log.error(msg)
                errors.append(msg)
            else:
                if 'include' in state:
                    if not isinstance(state['include'], list):
                        msg = ('Include Declaration in SLS \'{0}\' is not '
                               'formed as a list'.format(sls))
                        log.error(msg)
                        errors.append(msg)
                    else:
                        for sub_sls in state.pop('include'):
                            if isinstance(sub_sls, dict):
                                sub_sls, v = next(six.iteritems(sub_sls))
                                defaults = v.get('defaults', {})
                                key = v.get('key', None)
                            else:
                                key = None
                            if sub_sls not in mods:
                                nstate, mods, err = self.render_pstate(
                                        sub_sls,
                                        saltenv,
                                        mods,
                                        defaults
                                        )
                                if nstate:
                                    if key:
                                        nstate = {
                                            key: nstate
                                        }

                                    state = merge(
                                        state,
                                        nstate,
                                        self.merge_strategy,
                                        self.opts.get('renderer', 'yaml'),
                                        self.opts.get('pillar_merge_lists', False))

                                if err:
                                    errors += err
        return state, mods, errors