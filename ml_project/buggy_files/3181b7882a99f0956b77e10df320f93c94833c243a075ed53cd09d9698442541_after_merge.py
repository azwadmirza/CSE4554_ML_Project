    def _authenticate(self):
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
        if not acceptance_wait_time_max:
            acceptance_wait_time_max = acceptance_wait_time
        creds = None
        channel = salt.transport.client.AsyncReqChannel.factory(self.opts,
                                                                crypt='clear',
                                                                io_loop=self.io_loop)
        error = None
        while True:
            try:
                creds = yield self.sign_in(channel=channel)
            except SaltClientError as error:
                break
            if creds == 'retry':
                if self.opts.get('caller'):
                    print('Minion failed to authenticate with the master, '
                          'has the minion key been accepted?')
                    sys.exit(2)
                if acceptance_wait_time:
                    log.info('Waiting {0} seconds before retry.'.format(acceptance_wait_time))
                    yield tornado.gen.sleep(acceptance_wait_time)
                if acceptance_wait_time < acceptance_wait_time_max:
                    acceptance_wait_time += acceptance_wait_time
                    log.debug('Authentication wait time is {0}'.format(acceptance_wait_time))
                continue
            break
        if not isinstance(creds, dict) or 'aes' not in creds:
            try:
                del AsyncAuth.creds_map[self.__key(self.opts)]
            except KeyError:
                pass
            if not error:
                error = SaltClientError('Attempt to authenticate with the salt master failed')
            self._authenticate_future.set_exception(error)
        else:
            AsyncAuth.creds_map[self.__key(self.opts)] = creds
            self._creds = creds
            self._crypticle = Crypticle(self.opts, creds['aes'])
            self._authenticate_future.set_result(True)  # mark the sign-in as complete