    def run_wfunc(self):
        '''
        Execute a wrapper function

        Returns tuple of (json_data, '')
        '''
        # Ensure that opts/grains are up to date
        # Execute routine
        data_cache = self.opts.get('ssh_minion_cache', True)
        data = None
        cdir = os.path.join(self.opts['cachedir'], 'minions', self.id)
        if not os.path.isdir(cdir):
            os.makedirs(cdir)
        datap = os.path.join(cdir, 'data.p')
        refresh = False
        if not os.path.isfile(datap):
            refresh = True
        else:
            passed_time = (time.time() - os.stat(datap).st_mtime) / 60
            if passed_time > self.opts.get('cache_life', 60):
                refresh = True

        if self.opts.get('refresh_cache'):
            refresh = True
        conf_grains = {}
        #Save conf file grains before they get clobbered
        if 'ssh_grains' in self.opts:
            conf_grains = self.opts['ssh_grains']
        if not data_cache:
            refresh = True
        if refresh:
            # Make the datap
            # TODO: Auto expire the datap
            pre_wrapper = salt.client.ssh.wrapper.FunctionWrapper(
                self.opts,
                self.id,
                **self.target)
            opts_pkg = pre_wrapper['test.opts_pkg']()
            opts_pkg['file_roots'] = self.opts['file_roots']
            opts_pkg['pillar_roots'] = self.opts['pillar_roots']
            # Use the ID defined in the roster file
            opts_pkg['id'] = self.id

            if '_error' in opts_pkg:
                #Refresh failed
                ret = json.dumps({'local': opts_pkg['_error']})
                return ret

            pillar = salt.pillar.Pillar(
                    opts_pkg,
                    opts_pkg['grains'],
                    opts_pkg['id'],
                    opts_pkg.get('environment', 'base')
                    )

            pillar_data = pillar.compile_pillar()

            # TODO: cache minion opts in datap in master.py
            data = {'opts': opts_pkg,
                    'grains': opts_pkg['grains'],
                    'pillar': pillar_data}
            if data_cache:
                with salt.utils.fopen(datap, 'w+b') as fp_:
                    fp_.write(
                            self.serial.dumps(data)
                            )
        if not data and data_cache:
            with salt.utils.fopen(datap, 'rb') as fp_:
                data = self.serial.load(fp_)
        opts = data.get('opts', {})
        opts['grains'] = data.get('grains')

        #Restore master grains
        for grain in conf_grains:
            opts['grains'][grain] = conf_grains[grain]
        #Enable roster grains support
        if 'grains' in self.target:
            for grain in self.target['grains']:
                opts['grains'][grain] = self.target['grains'][grain]

        opts['pillar'] = data.get('pillar')
        wrapper = salt.client.ssh.wrapper.FunctionWrapper(
            opts,
            self.id,
            **self.target)
        self.wfuncs = salt.loader.ssh_wrapper(opts, wrapper, self.opts)
        wrapper.wfuncs = self.wfuncs
        result = self.wfuncs[self.fun](*self.args, **self.kwargs)
        # Mimic the json data-structure that "salt-call --local" will
        # emit (as seen in ssh_py_shim.py)
        if 'local' in result:
            ret = json.dumps({'local': result['local']})
        else:
            ret = json.dumps({'local': {'return': result}})
        return ret