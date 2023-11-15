    def render_GET(self, request):
        """
        .. http:get:: /wallets

        A GET request to this endpoint will return information about all available wallets in Tribler.
        This includes information about the address, a human-readable wallet name and the balance.

            **Example request**:

            .. sourcecode:: none

                curl -X GET http://localhost:8085/wallets

            **Example response**:

            .. sourcecode:: javascript

                {
                    "wallets": [{
                        "created": True,
                        "name": "Bitcoin",
                        "address": "17AVS7n3zgBjPq1JT4uVmEXdcX3vgB2wAh",
                        "balance": {
                            "available": 0.000126,
                            "pending": 0.0,
                            "currency": "BTC"
                        }
                    }, ...]
                }
        """
        wallets = {}
        balance_deferreds = []
        for wallet_id in self.session.lm.market_community.get_wallet_ids():
            wallet = self.session.lm.market_community.wallets[wallet_id]
            wallets[wallet_id] = {'created': wallet.created, 'address': wallet.get_address(), 'name': wallet.get_name()}
            balance_deferreds.append(wallet.get_balance().addCallback(
                lambda balance, wid=wallet_id: (wid, balance)))

        def on_received_balances(balances):
            for _, balance_info in balances:
                wallets[balance_info[0]]['balance'] = balance_info[1]

            request.write(json.dumps({"wallets": wallets}))
            request.finish()

        balance_deferred_list = DeferredList(balance_deferreds)
        balance_deferred_list.addCallback(on_received_balances)

        return NOT_DONE_YET