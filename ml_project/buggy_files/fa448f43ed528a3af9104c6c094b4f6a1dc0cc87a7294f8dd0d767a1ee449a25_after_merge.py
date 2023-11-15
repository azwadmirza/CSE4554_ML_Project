    def check_requisite(self, low, running, chunks, pre=False):
        '''
        Look into the running data to check the status of all requisite
        states
        '''
        present = False
        # If mod_watch is not available make it a require
        if 'watch' in low:
            if '{0}.mod_watch'.format(low['state']) not in self.states:
                if 'require' in low:
                    low['require'].extend(low.pop('watch'))
                else:
                    low['require'] = low.pop('watch')
            else:
                present = True
        if 'require' in low:
            present = True
        if 'prerequired' in low:
            present = True
        if 'prereq' in low:
            present = True
        if 'onfail' in low:
            present = True
        if 'onchanges' in low:
            present = True
        if not present:
            return 'met', ()
        self.reconcile_procs(running)
        reqs = {
                'require': [],
                'watch': [],
                'prereq': [],
                'onfail': [],
                'onchanges': []}
        if pre:
            reqs['prerequired'] = []
        for r_state in reqs:
            if r_state in low and low[r_state] is not None:
                for req in low[r_state]:
                    if isinstance(req, six.string_types):
                        req = {'id': req}
                    req = trim_req(req)
                    found = False
                    for chunk in chunks:
                        req_key = next(iter(req))
                        req_val = req[req_key]
                        if req_val is None:
                            continue
                        if req_key == 'sls':
                            # Allow requisite tracking of entire sls files
                            if fnmatch.fnmatch(chunk['__sls__'], req_val):
                                found = True
                                reqs[r_state].append(chunk)
                            continue
                        try:
                            if isinstance(req_val, six.string_types):
                                if (fnmatch.fnmatch(chunk['name'], req_val) or
                                        fnmatch.fnmatch(chunk['__id__'], req_val)):
                                    if req_key == 'id' or chunk['state'] == req_key:
                                        found = True
                                        reqs[r_state].append(chunk)
                            else:
                                raise KeyError
                        except KeyError as exc:
                            raise SaltRenderError(
                                'Could not locate requisite of [{0}] present in state with name [{1}]'.format(
                                    req_key, chunk['name']))
                        except TypeError:
                            # On Python 2, the above req_val, being an OrderedDict, will raise a KeyError,
                            # however on Python 3 it will raise a TypeError
                            # This was found when running tests.unit.test_state.StateCompilerTestCase.test_render_error_on_invalid_requisite
                            raise SaltRenderError(
                                'Could not locate requisite of [{0}] present in state with name [{1}]'.format(
                                    req_key, chunk['name']))
                    if not found:
                        return 'unmet', ()
        fun_stats = set()
        for r_state, chunks in six.iteritems(reqs):
            if r_state == 'prereq':
                run_dict = self.pre
            else:
                run_dict = running
            for chunk in chunks:
                tag = _gen_tag(chunk)
                if tag not in run_dict:
                    fun_stats.add('unmet')
                    continue
                if run_dict[tag].get('proc'):
                    # Run in parallel, first wait for a touch and then recheck
                    run_dict[tag].get('proc').join()
                if r_state == 'onfail':
                    if run_dict[tag]['result'] is True:
                        fun_stats.add('onfail')  # At least one state is OK
                        continue
                else:
                    if run_dict[tag]['result'] is False:
                        fun_stats.add('fail')
                        continue
                if r_state == 'onchanges':
                    if not run_dict[tag]['changes']:
                        fun_stats.add('onchanges')
                    else:
                        fun_stats.add('onchangesmet')
                    continue
                if r_state == 'watch' and run_dict[tag]['changes']:
                    fun_stats.add('change')
                    continue
                if r_state == 'prereq' and run_dict[tag]['result'] is None:
                    fun_stats.add('premet')
                if r_state == 'prereq' and not run_dict[tag]['result'] is None:
                    fun_stats.add('pre')
                else:
                    if run_dict[tag].get('__state_ran__', True):
                        fun_stats.add('met')

        if 'unmet' in fun_stats:
            status = 'unmet'
        elif 'fail' in fun_stats:
            status = 'fail'
        elif 'pre' in fun_stats:
            if 'premet' in fun_stats:
                status = 'met'
            else:
                status = 'pre'
        elif 'onfail' in fun_stats and 'met' not in fun_stats:
            status = 'onfail'  # all onfail states are OK
        elif 'onchanges' in fun_stats and 'onchangesmet' not in fun_stats:
            status = 'onchanges'
        elif 'change' in fun_stats:
            status = 'change'
        else:
            status = 'met'

        return status, reqs