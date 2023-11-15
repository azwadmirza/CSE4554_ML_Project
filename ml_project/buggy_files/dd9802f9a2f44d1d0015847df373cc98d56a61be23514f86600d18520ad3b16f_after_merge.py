    def _crypted_transfer(self, load, tries=3, timeout=60, payload='aes'):
        '''
        In case of authentication errors, try to renegotiate authentication
        and retry the method.
        Indeed, we can fail too early in case of a master restart during a
        minion state execution call
        '''
        def _do_transfer():
            return self.auth.crypticle.loads(
                self.sreq.send(payload,
                               self.auth.crypticle.dumps(load),
                               tries,
                               timeout)
            )
        try:
            return _do_transfer()
        except salt.crypt.AuthenticationError:
            self.auth = salt.crypt.SAuth(self.opts)
            return _do_transfer()