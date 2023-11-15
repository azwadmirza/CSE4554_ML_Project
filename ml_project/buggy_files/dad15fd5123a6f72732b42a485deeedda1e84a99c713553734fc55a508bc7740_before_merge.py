    def _verify_signature(self, payload, signing_input, header, signature,
                          key='', algorithms=None):

        alg = header['alg']

        if algorithms is not None and alg not in algorithms:
            raise InvalidAlgorithmError('The specified alg value is not allowed')

        try:
            alg_obj = self._algorithms[alg]
            key = alg_obj.prepare_key(key)

            if not alg_obj.verify(signing_input, key, signature):
                raise DecodeError('Signature verification failed')

        except KeyError:
            raise InvalidAlgorithmError('Algorithm not supported')