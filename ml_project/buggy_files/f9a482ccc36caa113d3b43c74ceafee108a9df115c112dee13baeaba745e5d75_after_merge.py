    def from_public_key_recovery(klass, signature, data, curve, hashfunc=sha1, sigdecode=sigdecode_string):
        # Given a signature and corresponding message this function
        # returns a list of verifying keys for this signature and message
        
        digest = hashfunc(data).digest()
        return klass.from_public_key_recovery_with_digest(signature, digest, curve, hashfunc=sha1, sigdecode=sigdecode)