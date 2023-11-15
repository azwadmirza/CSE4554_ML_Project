    def run(self):
        '''
        Execute the batch run
        '''
        args = [[],
                self.opts['fun'],
                self.opts['arg'],
                self.opts['timeout'],
                'list',
                ]
        bnum = self.get_bnum()
        # No targets to run
        if not self.minions:
            return
        to_run = copy.deepcopy(self.minions)
        active = []
        ret = {}
        iters = []
        # wait the specified time before decide a job is actually done
        bwait = self.opts.get('batch_wait', 0)
        wait = []

        if self.options:
            show_jid = self.options.show_jid
            show_verbose = self.options.verbose
        else:
            show_jid = False
            show_verbose = False

        # the minion tracker keeps track of responses and iterators
        # - it removes finished iterators from iters[]
        # - if a previously detected minion does not respond, its
        #   added with an empty answer to ret{} once the timeout is reached
        # - unresponsive minions are removed from active[] to make
        #   sure that the main while loop finishes even with unresp minions
        minion_tracker = {}

        # Iterate while we still have things to execute
        while len(ret) < len(self.minions):
            next_ = []
            if bwait and wait:
                self.__update_wait(wait)
            if len(to_run) <= bnum - len(wait) and not active:
                # last bit of them, add them all to next iterator
                while to_run:
                    next_.append(to_run.pop())
            else:
                for i in range(bnum - len(active) - len(wait)):
                    if to_run:
                        minion_id = to_run.pop()
                        if isinstance(minion_id, dict):
                            next_.append(minion_id.keys()[0])
                        else:
                            next_.append(minion_id)

            active += next_
            args[0] = next_

            if next_:
                if not self.quiet:
                    print_cli('\nExecuting run on {0}\n'.format(next_))
                # create a new iterator for this batch of minions
                new_iter = self.local.cmd_iter_no_block(
                                *args,
                                raw=self.opts.get('raw', False),
                                ret=self.opts.get('return', ''),
                                show_jid=show_jid,
                                verbose=show_verbose,
                                **self.eauth)
                # add it to our iterators and to the minion_tracker
                iters.append(new_iter)
                minion_tracker[new_iter] = {}
                # every iterator added is 'active' and has its set of minions
                minion_tracker[new_iter]['minions'] = next_
                minion_tracker[new_iter]['active'] = True

            else:
                time.sleep(0.02)
            parts = {}

            # see if we found more minions
            for ping_ret in self.ping_gen:
                if ping_ret is None:
                    break
                m = next(ping_ret.iterkeys())
                if m not in self.minions:
                    self.minions.append(m)
                    to_run.append(m)

            for queue in iters:
                try:
                    # Gather returns until we get to the bottom
                    ncnt = 0
                    while True:
                        part = next(queue)
                        if part is None:
                            time.sleep(0.01)
                            ncnt += 1
                            if ncnt > 5:
                                break
                            continue
                        if self.opts.get('raw'):
                            parts.update({part['id']: part})
                            minion_tracker[queue]['minions'].remove(part['id'])
                        else:
                            parts.update(part)
                            for id in part.keys():
                                if id in minion_tracker[queue]['minions']:
                                    minion_tracker[queue]['minions'].remove(id)
                except StopIteration:
                    # if a iterator is done:
                    # - set it to inactive
                    # - add minions that have not responded to parts{}

                    # check if the tracker contains the iterator
                    if queue in minion_tracker:
                        minion_tracker[queue]['active'] = False

                        # add all minions that belong to this iterator and
                        # that have not responded to parts{} with an empty response
                        for minion in minion_tracker[queue]['minions']:
                            if minion not in parts:
                                parts[minion] = {}
                                parts[minion]['ret'] = {}

            for minion, data in six.iteritems(parts):
                if minion in active:
                    active.remove(minion)
                    if bwait:
                        wait.append(datetime.now() + timedelta(seconds=bwait))
                if self.opts.get('raw'):
                    yield data
                elif self.opts.get('failhard'):
                    # When failhard is passed, we need to return all data to include
                    # the retcode to use in salt/cli/salt.py later. See issue #24996.
                    ret[minion] = data
                    yield {minion: data}
                else:
                    ret[minion] = data['ret']
                    yield {minion: data['ret']}
                if not self.quiet:
                    ret[minion] = data['ret']
                    data[minion] = data.pop('ret')
                    if 'out' in data:
                        out = data.pop('out')
                    else:
                        out = None
                    salt.output.display_output(
                            data,
                            out,
                            self.opts)

            # remove inactive iterators from the iters list
            for queue in minion_tracker:
                # only remove inactive queues
                if not minion_tracker[queue]['active'] and queue in iters:
                    iters.remove(queue)
                    # also remove the iterator's minions from the active list
                    for minion in minion_tracker[queue]['minions']:
                        if minion in active:
                            active.remove(minion)
                            if bwait:
                                wait.append(datetime.now() + timedelta(seconds=bwait))