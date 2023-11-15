    def _call_parallel_target(self, cdata, low):
        '''
        The target function to call that will create the parallel thread/process
        '''
        # we need to re-record start/end duration here because it is impossible to
        # correctly calculate further down the chain
        utc_start_time = datetime.datetime.utcnow()

        tag = _gen_tag(low)
        try:
            ret = self.states[cdata['full']](*cdata['args'],
                                             **cdata['kwargs'])
        except Exception:
            trb = traceback.format_exc()
            # There are a number of possibilities to not have the cdata
            # populated with what we might have expected, so just be smart
            # enough to not raise another KeyError as the name is easily
            # guessable and fallback in all cases to present the real
            # exception to the user
            if len(cdata['args']) > 0:
                name = cdata['args'][0]
            elif 'name' in cdata['kwargs']:
                name = cdata['kwargs']['name']
            else:
                name = low.get('name', low.get('__id__'))
            ret = {
                'result': False,
                'name': name,
                'changes': {},
                'comment': 'An exception occurred in this state: {0}'.format(
                    trb)
            }

        utc_finish_time = datetime.datetime.utcnow()
        delta = (utc_finish_time - utc_start_time)
        # duration in milliseconds.microseconds
        duration = (delta.seconds * 1000000 + delta.microseconds)/1000.0
        ret['duration'] = duration


        troot = os.path.join(self.opts['cachedir'], self.jid)
        tfile = os.path.join(troot, _clean_tag(tag))
        if not os.path.isdir(troot):
            try:
                os.makedirs(troot)
            except OSError:
                # Looks like the directory was created between the check
                # and the attempt, we are safe to pass
                pass
        with salt.utils.fopen(tfile, 'wb+') as fp_:
            fp_.write(msgpack.dumps(ret))