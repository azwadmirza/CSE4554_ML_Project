    def call_highstate(self, exclude=None, cache=None, cache_name='highstate',
                       force=False):
        '''
        Run the sequence to execute the salt highstate for this minion
        '''
        #Check that top file exists
        tag_name = 'no_|-states_|-states_|-None'
        ret = {tag_name: {
                'result': False,
                'comment': 'No states found for this minion',
                'name': 'No States',
                'changes': {},
                '__run_num__': 0,
        }}
        cfn = os.path.join(
                self.opts['cachedir'],
                '{0}.cache.p'.format(cache_name)
        )

        if cache:
            if os.path.isfile(cfn):
                with salt.utils.fopen(cfn, 'r') as fp_:
                    high = self.serial.load(fp_)
                    return self.state.call_high(high)
        #File exists so continue
        err = []
        try:
            top = self.get_top()
        except Exception:
            trb = traceback.format_exc()
            err.append(trb)
            return err
        err += self.verify_tops(top)
        matches = self.top_matches(top)
        if not matches:
            msg = ('No Top file or external nodes data matches found')
            ret[tag_name]['comment'] = msg
            return ret
        self.load_dynamic(matches)
        if not self._check_pillar(force):
            err += ['Pillar failed to render with the following messages:']
            err += self.state.opts['pillar']['_errors']
        else:
            high, errors = self.render_highstate(matches)
            if exclude:
                if isinstance(exclude, str):
                    exclude = exclude.split(',')
                if '__exclude__' in high:
                    high['__exclude__'].extend(exclude)
                else:
                    high['__exclude__'] = exclude
            err += errors
        if err:
            return err
        if not high:
            return ret
        with salt.utils.fopen(cfn, 'w+') as fp_:
            try:
                self.serial.dump(high, fp_)
            except TypeError:
                # Can't serialize pydsl
                pass
        return self.state.call_high(high)