def shell_jobber(self):
    '''
    Shell jobber start!
    '''
    while self.fun.value:
        msg = self.fun.value.popleft()
        data = msg.get('pub')
        match = getattr(
                self.matcher.value,
                '{0}_match'.format(
                    data.get('tgt_type', 'glob')
                    )
                )(data['tgt'])
        if not match:
            continue
        fun = data['fun']
        if fun in self.modules.value:
            func = self.modules.value[fun]
        else:
            continue
        args, kwargs = salt.minion.load_args_and_kwargs(
            func,
            salt.utils.args.parse_input(
                data['arg'],
                no_parse=data.get('no_parse', [])),
            data)
        cmd = ['salt-call',
               '--out', 'json',
               '--metadata',
               '-c', salt.syspaths.CONFIG_DIR]
        if 'return' in data:
            cmd.append('--return')
            cmd.append(data['return'])
        cmd.append(fun)
        for arg in args:
            cmd.append(arg)
        for key in kwargs:
            cmd.append('{0}={1}'.format(key, kwargs[key]))
        que = {'pub': data,
               'msg': msg}
        que['proc'] = subprocess.Popen(
                cmd,
                shell=False,
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE)
        self.shells.value[data['jid']] = que