    def _hash(self, secret, salt, rounds):
        if rounds is None:
            saltstring = "$%s$%s" % (self.algo_data.crypt_id, salt)
        else:
            saltstring = "$%s$rounds=%d$%s" % (self.algo_data.crypt_id, rounds, salt)
        result = crypt.crypt(secret, saltstring)

        # crypt.crypt returns None if it cannot parse saltstring
        # None as result would be interpreted by the some modules (user module)
        # as no password at all.
        if not result:
            raise AnsibleError("crypt.crypt does not support '%s' algorithm" % self.algorithm)

        return result