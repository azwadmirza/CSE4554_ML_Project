    def get_init_detail(self, params=None, user=None):
        """
        At the end of the initialization we return the certificate and the
        PKCS12 file, if the private key exists.
        """
        response_detail = TokenClass.get_init_detail(self, params, user)
        params = params or {}
        certificate = self.get_tokeninfo("certificate")
        response_detail["certificate"] = certificate
        privatekey = self.get_tokeninfo("privatekey")
        # If there is a private key, we dump a PKCS12
        if privatekey:
            response_detail["pkcs12"] = b64encode_and_unicode(self._create_pkcs12_bin())

        return response_detail