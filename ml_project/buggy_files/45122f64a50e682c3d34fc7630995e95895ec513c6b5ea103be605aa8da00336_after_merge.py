    def render_state(self, sls, saltenv, mods, matches, local=False):
        '''
        Render a state file and retrieve all of the include states
        '''
        errors = []
        if not local:
            state_data = self.client.get_state(sls, saltenv)
            fn_ = state_data.get('dest', False)
        else:
            fn_ = sls
            if not os.path.isfile(fn_):
                errors.append(
                    'Specified SLS {0} on local filesystem cannot '
                    'be found.'.format(sls)
                )
        if not fn_:
            errors.append(
                'Specified SLS {0} in saltenv {1} is not '
                'available on the salt master or through a configured '
                'fileserver'.format(sls, saltenv)
            )
        state = None
        try:
            state = compile_template(
                fn_, self.state.rend, self.state.opts['renderer'], saltenv,
                sls, rendered_sls=mods
            )
        except SaltRenderError as exc:
            msg = 'Rendering SLS \'{0}:{1}\' failed: {2}'.format(
                saltenv, sls, exc
            )
            log.critical(msg)
            errors.append(msg)
        except Exception as exc:
            msg = 'Rendering SLS {0} failed, render error: {1}'.format(
                sls, exc
            )
            log.critical(
                msg,
                # Show the traceback if the debug logging level is enabled
                exc_info_on_loglevel=logging.DEBUG
            )
            errors.append('{0}\n{1}'.format(msg, traceback.format_exc()))
        try:
            mods.add('{0}:{1}'.format(saltenv, sls))
        except AttributeError:
            pass
        if state:
            if not isinstance(state, dict):
                errors.append(
                    'SLS {0} does not render to a dictionary'.format(sls)
                )
            else:
                include = []
                if 'include' in state:
                    if not isinstance(state['include'], list):
                        err = ('Include Declaration in SLS {0} is not formed '
                               'as a list'.format(sls))
                        errors.append(err)
                    else:
                        include = state.pop('include')

                self._handle_extend(state, sls, saltenv, errors)
                self._handle_exclude(state, sls, saltenv, errors)
                self._handle_state_decls(state, sls, saltenv, errors)

                for inc_sls in include:
                    # inc_sls may take the form of:
                    #   'sls.to.include' <- same as {<saltenv>: 'sls.to.include'}
                    #   {<env_key>: 'sls.to.include'}
                    #   {'_xenv': 'sls.to.resolve'}
                    xenv_key = '_xenv'

                    if isinstance(inc_sls, dict):
                        env_key, inc_sls = inc_sls.popitem()
                    else:
                        env_key = saltenv

                    if env_key not in self.avail:
                        msg = ('Nonexistent saltenv {0!r} found in include '
                               'of {1!r} within SLS \'{2}:{3}\''
                               .format(env_key, inc_sls, saltenv, sls))
                        log.error(msg)
                        errors.append(msg)
                        continue

                    if inc_sls.startswith('.'):
                        p_comps = sls.split('.')
                        if state_data.get('source', '').endswith('/init.sls'):
                            inc_sls = sls + inc_sls
                        else:
                            inc_sls = '.'.join(p_comps[:-1]) + inc_sls

                    if env_key != xenv_key:
                        if matches is None:
                            matches = []
                        # Resolve inc_sls in the specified environment
                        if env_key in matches or fnmatch.filter(self.avail[env_key], inc_sls):
                            resolved_envs = [env_key]
                        else:
                            resolved_envs = []
                    else:
                        # Resolve inc_sls in the subset of environment matches
                        resolved_envs = [
                            aenv for aenv in matches
                            if fnmatch.filter(self.avail[aenv], inc_sls)
                        ]

                    # An include must be resolved to a single environment, or
                    # the include must exist in the current environment
                    if len(resolved_envs) == 1 or saltenv in resolved_envs:
                        # Match inc_sls against the available states in the
                        # resolved env, matching wildcards in the process. If
                        # there were no matches, then leave inc_sls as the
                        # target so that the next recursion of render_state
                        # will recognize the error.
                        sls_targets = fnmatch.filter(
                            self.avail[saltenv],
                            inc_sls
                        ) or [inc_sls]

                        for sls_target in sls_targets:
                            r_env = resolved_envs[0] if len(resolved_envs) == 1 else saltenv
                            mod_tgt = '{0}:{1}'.format(r_env, sls_target)
                            if mod_tgt not in mods:
                                nstate, err = self.render_state(
                                    sls_target,
                                    r_env,
                                    mods,
                                    matches
                                )
                                if nstate:
                                    self.merge_included_states(state, nstate, errors)
                                    state.update(nstate)
                                if err:
                                    errors.extend(err)
                    else:
                        msg = ''
                        if not resolved_envs:
                            msg = ('Unknown include: Specified SLS {0}: {1} is not available on the salt '
                                   'master in saltenv(s): {2} '
                                   ).format(env_key,
                                            inc_sls,
                                            ', '.join(matches) if env_key == xenv_key else env_key)
                        elif len(resolved_envs) > 1:
                            msg = ('Ambiguous include: Specified SLS {0}: {1} is available on the salt master '
                                   'in multiple available saltenvs: {2}'
                                   ).format(env_key,
                                            inc_sls,
                                            ', '.join(resolved_envs))
                        log.critical(msg)
                        errors.append(msg)
                try:
                    self._handle_iorder(state)
                except TypeError:
                    log.critical('Could not render SLS {0}. Syntax error detected.'.format(sls))
        else:
            state = {}
        return state, errors