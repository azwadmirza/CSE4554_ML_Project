    def get_as_dict(self):
        """
        This returns the token data as a dictionary.
        It is used to display the token list at /token/list.

        The certificate token can add the PKCS12 file if it exists

        :return: The token data as dict
        :rtype: dict
        """
        # first get the database values as dict
        token_dict = self.token.get()

        if "privatekey" in token_dict.get("info"):
            token_dict["info"]["pkcs12"] = base64.b64encode(
                self._create_pkcs12_bin())
            #del(token_dict["privatekey"])

        return token_dict