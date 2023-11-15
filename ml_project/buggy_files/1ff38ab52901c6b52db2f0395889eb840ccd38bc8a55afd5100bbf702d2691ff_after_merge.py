    def run(self, low):
        '''
        Execute the specified function in the specified state by passing the
        LowData
        '''
        l_fun = getattr(self, low['state'])
        f_call = salt.utils.format_call(l_fun, low)
        try:
            ret = l_fun(*f_call.get('args', ()), **f_call.get('kwargs', {}))
        except Exception:
            log.error(
                    'Failed to execute {0}: {1}\n'.format(low['state'], l_fun),
                    exc_info=True
                    )
            return False
        return ret