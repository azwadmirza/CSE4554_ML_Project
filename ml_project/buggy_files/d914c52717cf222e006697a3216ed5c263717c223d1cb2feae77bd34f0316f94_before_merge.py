    def call_chunk(self, low, running, chunks):
        '''
        Check if a chunk has any requires, execute the requires and then
        the chunk
        '''
        low = self._mod_aggregate(low, running, chunks)
        self._mod_init(low)
        tag = _gen_tag(low)
        if not low.get('prerequired'):
            self.active.add(tag)
        requisites = ['require', 'watch', 'prereq', 'onfail', 'onchanges']
        if not low.get('__prereq__'):
            requisites.append('prerequired')
            status, reqs = self.check_requisite(low, running, chunks, True)
        else:
            status, reqs = self.check_requisite(low, running, chunks)
        if status == 'unmet':
            lost = {}
            reqs = []
            for requisite in requisites:
                lost[requisite] = []
                if requisite not in low:
                    continue
                for req in low[requisite]:
                    if isinstance(req, six.string_types):
                        req = {'id': req}
                    req = trim_req(req)
                    found = False
                    req_key = next(iter(req))
                    req_val = req[req_key]
                    for chunk in chunks:
                        if req_val is None:
                            continue
                        if req_key == 'sls':
                            # Allow requisite tracking of entire sls files
                            if fnmatch.fnmatch(chunk['__sls__'], req_val):
                                if requisite == 'prereq':
                                    chunk['__prereq__'] = True
                                reqs.append(chunk)
                                found = True
                            continue
                        if (fnmatch.fnmatch(chunk['name'], req_val) or
                            fnmatch.fnmatch(chunk['__id__'], req_val)):
                            if req_key == 'id' or chunk['state'] == req_key:
                                if requisite == 'prereq':
                                    chunk['__prereq__'] = True
                                elif requisite == 'prerequired':
                                    chunk['__prerequired__'] = True
                                reqs.append(chunk)
                                found = True
                    if not found:
                        lost[requisite].append(req)
            if lost['require'] or lost['watch'] or lost['prereq'] or lost['onfail'] or lost['onchanges'] or lost.get('prerequired'):
                comment = 'The following requisites were not found:\n'
                for requisite, lreqs in six.iteritems(lost):
                    if not lreqs:
                        continue
                    comment += \
                        '{0}{1}:\n'.format(' ' * 19, requisite)
                    for lreq in lreqs:
                        req_key = next(iter(lreq))
                        req_val = lreq[req_key]
                        comment += \
                            '{0}{1}: {2}\n'.format(' ' * 23, req_key, req_val)
                running[tag] = {'changes': {},
                                'result': False,
                                'comment': comment,
                                '__run_num__': self.__run_num,
                                '__sls__': low['__sls__']}
                self.__run_num += 1
                self.event(running[tag], len(chunks), fire_event=low.get('fire_event'))
                return running
            for chunk in reqs:
                # Check to see if the chunk has been run, only run it if
                # it has not been run already
                ctag = _gen_tag(chunk)
                if ctag not in running:
                    if ctag in self.active:
                        if chunk.get('__prerequired__'):
                            # Prereq recusive, run this chunk with prereq on
                            if tag not in self.pre:
                                low['__prereq__'] = True
                                self.pre[ctag] = self.call(low, chunks, running)
                                return running
                            else:
                                return running
                        elif ctag not in running:
                            log.error('Recursive requisite found')
                            running[tag] = {
                                    'changes': {},
                                    'result': False,
                                    'comment': 'Recursive requisite found',
                                    '__run_num__': self.__run_num,
                                    '__sls__': low['__sls__']}
                        self.__run_num += 1
                        self.event(running[tag], len(chunks), fire_event=low.get('fire_event'))
                        return running
                    running = self.call_chunk(chunk, running, chunks)
                    if self.check_failhard(chunk, running):
                        running['__FAILHARD__'] = True
                        return running
            if low.get('__prereq__'):
                status, reqs = self.check_requisite(low, running, chunks)
                self.pre[tag] = self.call(low, chunks, running)
                if not self.pre[tag]['changes'] and status == 'change':
                    self.pre[tag]['changes'] = {'watch': 'watch'}
                    self.pre[tag]['result'] = None
            else:
                running = self.call_chunk(low, running, chunks)
            if self.check_failhard(chunk, running):
                running['__FAILHARD__'] = True
                return running
        elif status == 'met':
            if low.get('__prereq__'):
                self.pre[tag] = self.call(low, chunks, running)
            else:
                running[tag] = self.call(low, chunks, running)
        elif status == 'fail':
            # if the requisite that failed was due to a prereq on this low state
            # show the normal error
            if tag in self.pre:
                running[tag] = self.pre[tag]
                running[tag]['__run_num__'] = self.__run_num
                running[tag]['__sls__'] = low['__sls__']
            # otherwise the failure was due to a requisite down the chain
            else:
                # determine what the requisite failures where, and return
                # a nice error message
                failed_requisites = set()
                # look at all requisite types for a failure
                for req_lows in six.itervalues(reqs):
                    for req_low in req_lows:
                        req_tag = _gen_tag(req_low)
                        req_ret = self.pre.get(req_tag, running.get(req_tag))
                        # if there is no run output for the requisite it
                        # can't be the failure
                        if req_ret is None:
                            continue
                        # If the result was False (not None) it was a failure
                        if req_ret['result'] is False:
                            # use SLS.ID for the key-- so its easier to find
                            key = '{sls}.{_id}'.format(sls=req_low['__sls__'],
                                                       _id=req_low['__id__'])
                            failed_requisites.add(key)

                _cmt = 'One or more requisite failed: {0}'.format(
                    ', '.join(str(i) for i in failed_requisites)
                )
                running[tag] = {
                    'changes': {},
                    'result': False,
                    'comment': _cmt,
                    '__run_num__': self.__run_num,
                    '__sls__': low['__sls__']
                }
            self.__run_num += 1
        elif status == 'change' and not low.get('__prereq__'):
            ret = self.call(low, chunks, running)
            if not ret['changes'] and not ret.get('skip_watch', False):
                low = low.copy()
                low['sfun'] = low['fun']
                low['fun'] = 'mod_watch'
                low['__reqs__'] = reqs
                ret = self.call(low, chunks, running)
            running[tag] = ret
        elif status == 'pre':
            pre_ret = {'changes': {},
                       'result': True,
                       'comment': 'No changes detected',
                       '__run_num__': self.__run_num,
                       '__sls__': low['__sls__']}
            running[tag] = pre_ret
            self.pre[tag] = pre_ret
            self.__run_num += 1
        elif status == 'onfail':
            running[tag] = {'changes': {},
                            'result': True,
                            'comment': 'State was not run because onfail req did not change',
                            '__run_num__': self.__run_num,
                            '__sls__': low['__sls__']}
            self.__run_num += 1
        elif status == 'onchanges':
            running[tag] = {'changes': {},
                            'result': True,
                            'comment': 'State was not run because none of the onchanges reqs changed',
                            '__run_num__': self.__run_num,
                            '__sls__': low['__sls__']}
            self.__run_num += 1
        else:
            if low.get('__prereq__'):
                self.pre[tag] = self.call(low, chunks, running)
            else:
                running[tag] = self.call(low, chunks, running)
        if tag in running:
            self.event(running[tag], len(chunks), fire_event=low.get('fire_event'))
        return running