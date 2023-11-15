    def crypted_transfer_decode_dictentry(self, load, dictkey=None, tries=3, timeout=60):
        if not self.auth.authenticated:
            # Return controle back to the caller, continue when authentication succeeds
            yield self.auth.authenticate()
        # Return control to the caller. When send() completes, resume by populating ret with the Future.result
        ret = yield self.message_client.send(
            self._package_load(self.auth.crypticle.dumps(load)),
            timeout=timeout,
            tries=tries,
        )
        key = self.auth.get_keys()
        cipher = PKCS1_OAEP.new(key)
        if 'key' not in ret:
            # Reauth in the case our key is deleted on the master side.
            yield self.auth.authenticate()
            ret = yield self.message_client.send(
                self._package_load(self.auth.crypticle.dumps(load)),
                timeout=timeout,
                tries=tries,
            )
        aes = cipher.decrypt(ret['key'])
        pcrypt = salt.crypt.Crypticle(self.opts, aes)
        raise tornado.gen.Return(pcrypt.loads(ret[dictkey]))