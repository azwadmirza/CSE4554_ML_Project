    def authenticate(self, _=None):  # TODO: remove unused var
        '''
        Authenticate with the master, this method breaks the functional
        paradigm, it will update the master information from a fresh sign
        in, signing in can occur as often as needed to keep up with the
        revolving master AES key.

        :rtype: Crypticle
        :returns: A crypticle used for encryption operations
        '''
        acceptance_wait_time = self.opts['acceptance_wait_time']
        acceptance_wait_time_max = self.opts['acceptance_wait_time_max']
        channel = salt.transport.client.ReqChannel.factory(self.opts, crypt='clear')
        if not acceptance_wait_time_max:
            acceptance_wait_time_max = acceptance_wait_time
        while True:
            creds = self.sign_in(channel=channel)
            if creds == 'retry':
                if self.opts.get('caller'):
                    print('Minion failed to authenticate with the master, '
                          'has the minion key been accepted?')
                    sys.exit(2)
                if acceptance_wait_time:
                    log.info('Waiting {0} seconds before retry.'.format(acceptance_wait_time))
                    time.sleep(acceptance_wait_time)
                if acceptance_wait_time < acceptance_wait_time_max:
                    acceptance_wait_time += acceptance_wait_time
                    log.debug('Authentication wait time is {0}'.format(acceptance_wait_time))
                continue
            break
        self._creds = creds
        self._crypticle = Crypticle(self.opts, creds['aes'])