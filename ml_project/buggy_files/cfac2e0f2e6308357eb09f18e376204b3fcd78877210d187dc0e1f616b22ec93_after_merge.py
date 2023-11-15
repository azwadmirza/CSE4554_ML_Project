    def top_matches(self, top, reload=False):
        '''
        Search through the top high data for matches and return the states
        that this minion needs to execute.

        Returns:
        {'saltenv': ['state1', 'state2', ...]}

        reload
            Reload the matcher loader
        '''
        matches = {}
        if reload:
            self.matchers = salt.loader.matchers(self.opts)
        for saltenv, body in six.iteritems(top):
            if self.opts['pillarenv']:
                if saltenv != self.opts['pillarenv']:
                    continue
            for match, data in six.iteritems(body):
                if self.matchers['confirm_top.confirm_top'](
                        match,
                        data,
                        self.opts.get('nodegroups', {}),
                        ):
                    if saltenv not in matches:
                        matches[saltenv] = env_matches = []
                    else:
                        env_matches = matches[saltenv]
                    for item in data:
                        if isinstance(item, six.string_types) and item not in env_matches:
                            env_matches.append(item)
        return matches