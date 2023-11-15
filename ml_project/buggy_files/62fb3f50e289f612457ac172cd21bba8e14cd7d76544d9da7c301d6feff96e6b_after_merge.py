    def _hash(self, secret, salt, rounds):
        if rounds is None:
            saltstring = "$%s$%s" % (self.algo_data.crypt_id, salt)
        else:
            saltstring = "$%s$rounds=%d$%s" % (self.algo_data.crypt_id, rounds, salt)

        # crypt.crypt on Python < 3.9 returns None if it cannot parse saltstring
        # On Python >= 3.9, it throws OSError.
        try:
            result = crypt.crypt(secret, saltstring)
            orig_exc = None
        except OSError as e:
            result = None
            orig_exc = e

        # None as result would be interpreted by the some modules (user module)
        # as no password at all.
        if not result:
            raise AnsibleError(
                "crypt.crypt does not support '%s' algorithm" % self.algorithm,
                orig_exc=orig_exc,
            )

        return result