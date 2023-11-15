    def load_provider(self):
        provider = self._task.args.get('provider', {})
        for key, value in iteritems(ios_argument_spec):
            if key in self._task.args:
                provider[key] = self._task.args[key]
            elif 'fallback' in value:
                provider[key] = self._fallback(value['fallback'])
            elif key not in provider:
                provider[key] = None
        self._task.args['provider'] = provider