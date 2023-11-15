    def requisite_in(self, high):
        '''
        Extend the data reference with requisite_in arguments
        '''
        req_in = set([
            u'require_in',
            u'watch_in',
            u'onfail_in',
            u'onchanges_in',
            u'use',
            u'use_in',
            u'prereq',
            u'prereq_in',
            ])
        req_in_all = req_in.union(
                set([
                    u'require',
                    u'watch',
                    u'onfail',
                    u'onfail_stop',
                    u'onchanges',
                    ]))
        extend = {}
        errors = []
        for id_, body in six.iteritems(high):
            if not isinstance(body, dict):
                continue
            for state, run in six.iteritems(body):
                if state.startswith(u'__'):
                    continue
                for arg in run:
                    if isinstance(arg, dict):
                        # It is not a function, verify that the arg is a
                        # requisite in statement
                        if len(arg) < 1:
                            # Empty arg dict
                            # How did we get this far?
                            continue
                        # Split out the components
                        key = next(iter(arg))
                        if key not in req_in:
                            continue
                        rkey = key.split(u'_')[0]
                        items = arg[key]
                        if isinstance(items, dict):
                            # Formatted as a single req_in
                            for _state, name in six.iteritems(items):

                                # Not a use requisite_in
                                found = False
                                if name not in extend:
                                    extend[name] = OrderedDict()
                                if u'.' in _state:
                                    errors.append(
                                        u'Invalid requisite in {0}: {1} for '
                                        u'{2}, in SLS \'{3}\'. Requisites must '
                                        u'not contain dots, did you mean \'{4}\'?'
                                        .format(
                                            rkey,
                                            _state,
                                            name,
                                            body[u'__sls__'],
                                            _state[:_state.find(u'.')]
                                        )
                                    )
                                    _state = _state.split(u'.')[0]
                                if _state not in extend[name]:
                                    extend[name][_state] = []
                                extend[name][u'__env__'] = body[u'__env__']
                                extend[name][u'__sls__'] = body[u'__sls__']
                                for ind in range(len(extend[name][_state])):
                                    if next(iter(
                                        extend[name][_state][ind])) == rkey:
                                        # Extending again
                                        extend[name][_state][ind][rkey].append(
                                                {state: id_}
                                                )
                                        found = True
                                if found:
                                    continue
                                # The rkey is not present yet, create it
                                extend[name][_state].append(
                                        {rkey: [{state: id_}]}
                                        )

                        if isinstance(items, list):
                            # Formed as a list of requisite additions
                            hinges = []
                            for ind in items:
                                if not isinstance(ind, dict):
                                    # Malformed req_in
                                    continue
                                if len(ind) < 1:
                                    continue
                                pstate = next(iter(ind))
                                pname = ind[pstate]
                                if pstate == u'sls':
                                    # Expand hinges here
                                    hinges = find_sls_ids(pname, high)
                                else:
                                    hinges.append((pname, pstate))
                                if u'.' in pstate:
                                    errors.append(
                                        u'Invalid requisite in {0}: {1} for '
                                        u'{2}, in SLS \'{3}\'. Requisites must '
                                        u'not contain dots, did you mean \'{4}\'?'
                                        .format(
                                            rkey,
                                            pstate,
                                            pname,
                                            body[u'__sls__'],
                                            pstate[:pstate.find(u'.')]
                                        )
                                    )
                                    pstate = pstate.split(u".")[0]
                                for tup in hinges:
                                    name, _state = tup
                                    if key == u'prereq_in':
                                        # Add prerequired to origin
                                        if id_ not in extend:
                                            extend[id_] = OrderedDict()
                                        if state not in extend[id_]:
                                            extend[id_][state] = []
                                        extend[id_][state].append(
                                                {u'prerequired': [{_state: name}]}
                                                )
                                    if key == u'prereq':
                                        # Add prerequired to prereqs
                                        ext_ids = find_name(name, _state, high)
                                        for ext_id, _req_state in ext_ids:
                                            if ext_id not in extend:
                                                extend[ext_id] = OrderedDict()
                                            if _req_state not in extend[ext_id]:
                                                extend[ext_id][_req_state] = []
                                            extend[ext_id][_req_state].append(
                                                    {u'prerequired': [{state: id_}]}
                                                    )
                                        continue
                                    if key == u'use_in':
                                        # Add the running states args to the
                                        # use_in states
                                        ext_ids = find_name(name, _state, high)
                                        for ext_id, _req_state in ext_ids:
                                            if not ext_id:
                                                continue
                                            ext_args = state_args(ext_id, _state, high)
                                            if ext_id not in extend:
                                                extend[ext_id] = OrderedDict()
                                            if _req_state not in extend[ext_id]:
                                                extend[ext_id][_req_state] = []
                                            ignore_args = req_in_all.union(ext_args)
                                            for arg in high[id_][state]:
                                                if not isinstance(arg, dict):
                                                    continue
                                                if len(arg) != 1:
                                                    continue
                                                if next(iter(arg)) in ignore_args:
                                                    continue
                                                # Don't use name or names
                                                if next(six.iterkeys(arg)) == u'name':
                                                    continue
                                                if next(six.iterkeys(arg)) == u'names':
                                                    continue
                                                extend[ext_id][_req_state].append(arg)
                                        continue
                                    if key == u'use':
                                        # Add the use state's args to the
                                        # running state
                                        ext_ids = find_name(name, _state, high)
                                        for ext_id, _req_state in ext_ids:
                                            if not ext_id:
                                                continue
                                            loc_args = state_args(id_, state, high)
                                            if id_ not in extend:
                                                extend[id_] = OrderedDict()
                                            if state not in extend[id_]:
                                                extend[id_][state] = []
                                            ignore_args = req_in_all.union(loc_args)
                                            for arg in high[ext_id][_req_state]:
                                                if not isinstance(arg, dict):
                                                    continue
                                                if len(arg) != 1:
                                                    continue
                                                if next(iter(arg)) in ignore_args:
                                                    continue
                                                # Don't use name or names
                                                if next(six.iterkeys(arg)) == u'name':
                                                    continue
                                                if next(six.iterkeys(arg)) == u'names':
                                                    continue
                                                extend[id_][state].append(arg)
                                        continue
                                    found = False
                                    if name not in extend:
                                        extend[name] = OrderedDict()
                                    if _state not in extend[name]:
                                        extend[name][_state] = []
                                    extend[name][u'__env__'] = body[u'__env__']
                                    extend[name][u'__sls__'] = body[u'__sls__']
                                    for ind in range(len(extend[name][_state])):
                                        if next(iter(
                                            extend[name][_state][ind])) == rkey:
                                            # Extending again
                                            extend[name][_state][ind][rkey].append(
                                                    {state: id_}
                                                    )
                                            found = True
                                    if found:
                                        continue
                                    # The rkey is not present yet, create it
                                    extend[name][_state].append(
                                            {rkey: [{state: id_}]}
                                            )
        high[u'__extend__'] = []
        for key, val in six.iteritems(extend):
            high[u'__extend__'].append({key: val})
        req_in_high, req_in_errors = self.reconcile_extend(high)
        errors.extend(req_in_errors)
        return req_in_high, errors