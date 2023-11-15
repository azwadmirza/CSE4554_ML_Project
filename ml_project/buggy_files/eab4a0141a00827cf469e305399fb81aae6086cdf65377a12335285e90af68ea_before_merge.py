    def call_chunk(self, low, running, chunks):
        '''
        Check if a chunk has any requires, execute the requires and then
        the chunk
        '''
        self._mod_init(low)
        tag = _gen_tag(low)
        if not low.get('prerequired'):
            self.active.add(tag)
        requisites = ['require', 'watch', 'prereq']
        if not low.get('__prereq__'):
            requisites.append('prerequired')
            status = self.check_requisite(low, running, chunks, True)
        else:
            status = self.check_requisite(low, running, chunks)
        if status == 'unmet':
            lost = {}
            reqs = []
            for requisite in requisites:
                lost[requisite] = []
                if requisite not in low:
                    continue
                for req in low[requisite]:
                    req = trim_req(req)
                    found = False
                    for chunk in chunks:
                        req_key = next(iter(req))
                        req_val = req[req_key]
                        if req_val is None:
                            continue
                        if (fnmatch.fnmatch(chunk['name'], req_val) or
                            fnmatch.fnmatch(chunk['__id__'], req_val)):
                            if chunk['state'] == req_key:
                                if requisite == 'prereq':
                                    chunk['__prereq__'] = True
                                elif requisite == 'prerequired':
                                    chunk['__prerequired__'] = True
                                reqs.append(chunk)
                                found = True
                        elif req_key == 'sls':
                            # Allow requisite tracking of entire sls files
                            if fnmatch.fnmatch(chunk['__sls__'], req_val):
                                if requisite == 'prereq':
                                    chunk['__prereq__'] = True
                                reqs.append(chunk)
                                found = True
                    if not found:
                        lost[requisite].append(req)
            if lost['require'] or lost['watch'] or lost['prereq'] or lost.get('prerequired'):
                comment = 'The following requisites were not found:\n'
                for requisite, lreqs in lost.items():
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
                                '__run_num__': self.__run_num}
                self.__run_num += 1
                self.event(running[tag])
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
                                self.pre[ctag] = self.call(low)
                                return running
                        elif ctag not in running:
                            log.error('Recursive requisite found')
                            running[tag] = {
                                    'changes': {},
                                    'result': False,
                                    'comment': 'Recursive requisite found',
                                    '__run_num__': self.__run_num}
                        self.__run_num += 1
                        self.event(running[tag])
                        return running
                    running = self.call_chunk(chunk, running, chunks)
                    if self.check_failhard(chunk, running):
                        running['__FAILHARD__'] = True
                        return running
            if low.get('__prereq__'):
                status = self.check_requisite(low, running, chunks)
                self.pre[tag] = self.call(low)
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
                self.pre[tag] = self.call(low)
            else:
                running[tag] = self.call(low)
        elif status == 'fail':
            running[tag] = {'changes': {},
                            'result': False,
                            'comment': 'One or more requisite failed',
                            '__run_num__': self.__run_num}
            self.__run_num += 1
        elif status == 'change' and not low.get('__prereq__'):
            ret = self.call(low)
            if not ret['changes']:
                low = low.copy()
                low['sfun'] = low['fun']
                low['fun'] = 'mod_watch'
                ret = self.call(low)
            running[tag] = ret
        elif status == 'pre':
            running[tag] = {'changes': {},
                            'result': True,
                            'comment': 'No changes detected',
                            '__run_num__': self.__run_num}
            self.__run_num += 1
        else:
            if low.get('__prereq__'):
                self.pre[tag] = self.call(low)
            else:
                running[tag] = self.call(low)
        self.event(running[tag])
        return running