    def run(self):
        '''
        Execute the routine, the routine can be either:
        1. Execute a remote Salt command
        2. Execute a raw shell command
        3. Execute a wrapper func
        '''
        if self.opts.get('raw_shell'):
            return self.shell.exec_cmd(self.arg_str)
        elif self.fun in self.wfuncs:
            # Ensure that opts/grains are up to date
            # Execute routine
            cdir = os.path.join(self.opts['cachedir'], 'minions', self.id)
            if not os.path.isdir(cdir):
                os.makedirs(cdir)
            datap = os.path.join(cdir, 'data.p')
            refresh = False
            if not os.path.isfile(datap):
                refresh = True
            else:
                passed_time = (time.time() - os.stat(datap).st_mtime) / 60
                if (passed_time > self.opts.get('cache_life', 60)):
                    refresh = True
            if self.opts.get('refresh_cache'):
                refresh = True
            if refresh:
                # Make the datap
                # TODO: Auto expire the datap
                pre_wrapper = salt.client.ssh.wrapper.FunctionWrapper(
                    self.opts,
                    self.id,
                    **self.target)
                opts_pkg = pre_wrapper['test.opts_pkg']()
                pillar = salt.pillar.Pillar(
                        opts_pkg,
                        opts_pkg['grains'],
                        opts_pkg['id'],
                        opts_pkg.get('environment', 'base')
                        )
                pillar_data = pillar.compile_pillar()

                # TODO: cache minion opts in datap in master.py
                with salt.utils.fopen(datap, 'w+') as fp_:
                    fp_.write(
                            self.serial.dumps(
                                {'opts': opts_pkg,
                                 'grains': opts_pkg['grains'],
                                 'pillar': pillar_data}
                                )
                            )
            with salt.utils.fopen(datap, 'r') as fp_:
                data = self.serial.load(fp_)
            opts = data.get('opts', {})
            opts['grains'] = data.get('grains')
            opts['pillar'] = data.get('pillar')
            wrapper = salt.client.ssh.wrapper.FunctionWrapper(
                opts,
                self.id,
                **self.target)
            self.wfuncs = salt.loader.ssh_wrapper(opts, wrapper)
            wrapper.wfuncs = self.wfuncs
            ret = json.dumps(self.wfuncs[self.fun](*self.arg))
            return ret, ''
        else:
            return self.cmd_block()