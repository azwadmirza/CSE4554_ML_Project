    def load_modules(self, data=None, proxy=None):
        '''
        Load the modules into the state
        '''
        log.info('Loading fresh modules for state activity')
        self.utils = salt.loader.utils(self.opts)
        self.functions = salt.loader.minion_mods(self.opts, self.state_con,
                                                 utils=self.utils,
                                                 proxy=self.proxy)
        if isinstance(data, dict):
            if data.get('provider', False):
                if isinstance(data['provider'], str):
                    providers = [{data['state']: data['provider']}]
                elif isinstance(data['provider'], list):
                    providers = data['provider']
                else:
                    providers = {}
                for provider in providers:
                    for mod in provider:
                        funcs = salt.loader.raw_mod(self.opts,
                                provider[mod],
                                self.functions)
                        if funcs:
                            for func in funcs:
                                f_key = '{0}{1}'.format(
                                        mod,
                                        func[func.rindex('.'):]
                                        )
                                self.functions[f_key] = funcs[func]
        self.serializers = salt.loader.serializers(self.opts)
        self._load_states()
        self.rend = salt.loader.render(self.opts, self.functions, states=self.states)