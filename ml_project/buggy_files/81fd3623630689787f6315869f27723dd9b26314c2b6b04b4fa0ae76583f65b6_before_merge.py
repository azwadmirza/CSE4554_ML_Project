    def call_listen(self, chunks, running):
        '''
        Find all of the listen routines and call the associated mod_watch runs
        '''
        listeners = []
        crefs = {}
        for chunk in chunks:
            crefs[(chunk[u'state'], chunk[u'name'])] = chunk
            crefs[(chunk[u'state'], chunk[u'__id__'])] = chunk
            if u'listen' in chunk:
                listeners.append({(chunk[u'state'], chunk[u'__id__']): chunk[u'listen']})
            if u'listen_in' in chunk:
                for l_in in chunk[u'listen_in']:
                    for key, val in six.iteritems(l_in):
                        listeners.append({(key, val): [{chunk[u'state']: chunk[u'__id__']}]})
        mod_watchers = []
        errors = {}
        for l_dict in listeners:
            for key, val in six.iteritems(l_dict):
                for listen_to in val:
                    if not isinstance(listen_to, dict):
                        continue
                    for lkey, lval in six.iteritems(listen_to):
                        if (lkey, lval) not in crefs:
                            rerror = {_l_tag(lkey, lval):
                                      {
                                          u'comment': u'Referenced state {0}: {1} does not exist'.format(lkey, lval),
                                          u'name': u'listen_{0}:{1}'.format(lkey, lval),
                                          u'result': False,
                                          u'changes': {}
                                      }}
                            errors.update(rerror)
                            continue
                        to_tag = _gen_tag(crefs[(lkey, lval)])
                        if to_tag not in running:
                            continue
                        if running[to_tag][u'changes']:
                            if key not in crefs:
                                rerror = {_l_tag(key[0], key[1]):
                                             {u'comment': u'Referenced state {0}: {1} does not exist'.format(key[0], key[1]),
                                              u'name': u'listen_{0}:{1}'.format(key[0], key[1]),
                                              u'result': False,
                                              u'changes': {}}}
                                errors.update(rerror)
                                continue
                            chunk = crefs[key]
                            low = chunk.copy()
                            low[u'sfun'] = chunk[u'fun']
                            low[u'fun'] = u'mod_watch'
                            low[u'__id__'] = u'listener_{0}'.format(low[u'__id__'])
                            for req in STATE_REQUISITE_KEYWORDS:
                                if req in low:
                                    low.pop(req)
                            mod_watchers.append(low)
        ret = self.call_chunks(mod_watchers)
        running.update(ret)
        for err in errors:
            errors[err][u'__run_num__'] = self.__run_num
            self.__run_num += 1
        running.update(errors)
        return running