    def render_PUT(self, request):
        """
        .. http:put:: /wallets/(string:wallet identifier)

        A request to this endpoint will create a new wallet.

            **Example request**:

            .. sourcecode:: none

                curl -X PUT http://localhost:8085/wallets/BTC --data "password=secret"

            **Example response**:

            .. sourcecode:: javascript

                {
                    "created": True
                }
        """
        if self.session.lm.market_community.wallets[self.identifier].created:
            request.setResponseCode(http.BAD_REQUEST)
            return json.dumps({"error": "this wallet already exists"})

        def on_wallet_created(_):
            request.write(json.dumps({"created": True}))
            request.finish()

        parameters = http.parse_qs(request.content.read(), 1)

        if self.identifier == "BTC" and 'password' not in parameters:
            request.setResponseCode(http.BAD_REQUEST)
            return json.dumps({"error": "a password is required when creating a Bitcoin wallet"})

        if self.identifier == "BTC":  # get the password
            if parameters['password'] and len(parameters['password']) > 0:
                password = parameters['password'][0]
                self.session.lm.market_community.wallets[self.identifier].create_wallet(password=password)\
                    .addCallback(on_wallet_created)
        else:
            self.session.lm.market_community.wallets[self.identifier].create_wallet().addCallback(on_wallet_created)

        return NOT_DONE_YET