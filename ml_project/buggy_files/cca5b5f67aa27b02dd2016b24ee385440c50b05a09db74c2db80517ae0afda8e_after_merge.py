    def run(self, low):
        '''
        Execute the specified function in the specified state by passing the
        low data
        '''
        l_fun = getattr(self, low['state'])
        try:
            f_call = salt.utils.format_call(l_fun, low)
            kwargs = f_call.get('kwargs', {})

            # TODO: Setting the user doesn't seem to work for actual remote publishes
            if low['state'] in ('runner', 'wheel'):
                # Update called function's low data with event user to
                # segregate events fired by reactor and avoid reaction loops
                kwargs['__user__'] = self.event_user
                # Replace ``state`` kwarg which comes from high data compiler.
                # It breaks some runner functions and seems unnecessary.
                kwargs['__state__'] = kwargs.pop('state')

            l_fun(*f_call.get('args', ()), **kwargs)
        except Exception:
            log.error(
                    'Failed to execute {0}: {1}\n'.format(low['state'], l_fun),
                    exc_info=True
                    )