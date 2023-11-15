    def __gen_opts(self, opts):
        '''
        The options used by the High State object are derived from options
        on the minion and the master, or just the minion if the high state
        call is entirely local.
        '''
        # If the state is intended to be applied locally, then the local opts
        # should have all of the needed data, otherwise overwrite the local
        # data items with data from the master
        if 'local_state' in opts:
            if opts['local_state']:
                return opts
        mopts = self.client.master_opts()
        if not isinstance(mopts, dict):
            # An error happened on the master
            opts['renderer'] = 'yaml_jinja'
            opts['failhard'] = False
            opts['state_top'] = 'salt://top.sls'
            opts['nodegroups'] = {}
            opts['file_roots'] = {'base': ['/srv/salt']}
        else:
            opts['renderer'] = mopts['renderer']
            opts['failhard'] = mopts.get('failhard', False)
            if mopts['state_top'].startswith('salt://'):
                opts['state_top'] = mopts['state_top']
            elif mopts['state_top'].startswith('/'):
                opts['state_top'] = os.path.join('salt://', mopts['state_top'][1:])
            else:
                opts['state_top'] = os.path.join('salt://', mopts['state_top'])
            opts['nodegroups'] = mopts.get('nodegroups', {})
            opts['file_roots'] = mopts['file_roots']
        return opts