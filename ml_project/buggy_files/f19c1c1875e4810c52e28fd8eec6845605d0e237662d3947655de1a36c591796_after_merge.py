    def _get_challenge_data(self, auth):
        '''
        Returns a dict with the data for all proposed (and supported) challenges
        of the given authorization.
        '''

        data = {}
        # no need to choose a specific challenge here as this module
        # is not responsible for fulfilling the challenges. Calculate
        # and return the required information for each challenge.
        for challenge in auth['challenges']:
            type = challenge['type']
            token = re.sub(r"[^A-Za-z0-9_\-]", "_", challenge['token'])
            keyauthorization = self.account.get_keyauthorization(token)

            # NOTE: tls-sni-01 is not supported by choice
            # too complex to be useful and tls-sni-02 is an alternative
            # as soon as it is implemented server side
            if type == 'http-01':
                # https://tools.ietf.org/html/draft-ietf-acme-acme-02#section-7.2
                resource = '.well-known/acme-challenge/' + token
                value = keyauthorization
            elif type == 'tls-sni-02':
                # https://tools.ietf.org/html/draft-ietf-acme-acme-02#section-7.3
                token_digest = hashlib.sha256(token.encode('utf8')).hexdigest()
                ka_digest = hashlib.sha256(keyauthorization.encode('utf8')).hexdigest()
                len_token_digest = len(token_digest)
                len_ka_digest = len(ka_digest)
                resource = 'subjectAlternativeNames'
                value = [
                    "{0}.{1}.token.acme.invalid".format(token_digest[:len_token_digest // 2], token_digest[len_token_digest // 2:]),
                    "{0}.{1}.ka.acme.invalid".format(ka_digest[:len_ka_digest // 2], ka_digest[len_ka_digest // 2:]),
                ]
            elif type == 'dns-01':
                # https://tools.ietf.org/html/draft-ietf-acme-acme-02#section-7.4
                resource = '_acme-challenge'
                value = nopad_b64(hashlib.sha256(to_bytes(keyauthorization)).digest())
            else:
                continue

            data[type] = {'resource': resource, 'resource_value': value}
        return data