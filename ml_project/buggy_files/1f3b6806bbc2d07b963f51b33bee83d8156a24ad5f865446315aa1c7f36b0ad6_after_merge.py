    async def jsonrpc_collection_create(
            self, name, bid, claims, allow_duplicate_name=False,
            channel_id=None, channel_name=None, channel_account_id=None,
            account_id=None, wallet_id=None, claim_address=None, funding_account_ids=None,
            preview=False, blocking=False, **kwargs):
        """
        Create a new collection.

        Usage:
            collection_create (<name> | --name=<name>) (<bid> | --bid=<bid>)
                   (<claims>... | --claims=<claims>...)
                   [--allow_duplicate_name]
                   [--title=<title>] [--description=<description>]
                   [--tags=<tags>...] [--languages=<languages>...] [--locations=<locations>...]
                   [--thumbnail_url=<thumbnail_url>]
                   [--account_id=<account_id>] [--wallet_id=<wallet_id>]
                   [--claim_address=<claim_address>] [--funding_account_ids=<funding_account_ids>...]
                   [--preview] [--blocking]

        Options:
            --name=<name>                  : (str) name of the collection
            --bid=<bid>                    : (decimal) amount to back the claim
            --claims=<claims>              : (list) claim ids to be included in the collection
            --allow_duplicate_name         : (bool) create new collection even if one already exists with
                                                    given name. default: false.
            --title=<title>                : (str) title of the collection
            --description=<description>    : (str) description of the collection
            --clear_languages              : (bool) clear existing languages (prior to adding new ones)
            --tags=<tags>                  : (list) content tags
            --clear_languages              : (bool) clear existing languages (prior to adding new ones)
            --languages=<languages>        : (list) languages used by the collection,
                                                    using RFC 5646 format, eg:
                                                    for English `--languages=en`
                                                    for Spanish (Spain) `--languages=es-ES`
                                                    for Spanish (Mexican) `--languages=es-MX`
                                                    for Chinese (Simplified) `--languages=zh-Hans`
                                                    for Chinese (Traditional) `--languages=zh-Hant`
            --locations=<locations>        : (list) locations of the collection, consisting of 2 letter
                                                    `country` code and a `state`, `city` and a postal
                                                    `code` along with a `latitude` and `longitude`.
                                                    for JSON RPC: pass a dictionary with aforementioned
                                                        attributes as keys, eg:
                                                        ...
                                                        "locations": [{'country': 'US', 'state': 'NH'}]
                                                        ...
                                                    for command line: pass a colon delimited list
                                                        with values in the following order:

                                                          "COUNTRY:STATE:CITY:CODE:LATITUDE:LONGITUDE"

                                                        making sure to include colon for blank values, for
                                                        example to provide only the city:

                                                          ... --locations="::Manchester"

                                                        with all values set:

                                                 ... --locations="US:NH:Manchester:03101:42.990605:-71.460989"

                                                        optionally, you can just pass the "LATITUDE:LONGITUDE":

                                                          ... --locations="42.990605:-71.460989"

                                                        finally, you can also pass JSON string of dictionary
                                                        on the command line as you would via JSON RPC

                                                          ... --locations="{'country': 'US', 'state': 'NH'}"

            --thumbnail_url=<thumbnail_url>: (str) thumbnail url
            --account_id=<account_id>      : (str) account to use for holding the transaction
            --wallet_id=<wallet_id>        : (str) restrict operation to specific wallet
            --funding_account_ids=<funding_account_ids>: (list) ids of accounts to fund this transaction
            --claim_address=<claim_address>: (str) address where the collection is sent to, if not specified
                                                   it will be determined automatically from the account
            --preview                      : (bool) do not broadcast the transaction
            --blocking                     : (bool) wait until transaction is in mempool

        Returns: {Transaction}
        """
        wallet = self.wallet_manager.get_wallet_or_default(wallet_id)
        account = wallet.get_account_or_default(account_id)
        funding_accounts = wallet.get_accounts_or_all(funding_account_ids)
        self.valid_collection_name_or_error(name)
        channel = await self.get_channel_or_none(wallet, channel_account_id, channel_id, channel_name, for_signing=True)
        amount = self.get_dewies_or_error('bid', bid, positive_value=True)
        claim_address = await self.get_receiving_address(claim_address, account)

        existing_collections = await self.ledger.get_collections(accounts=wallet.accounts, claim_name=name)
        if len(existing_collections) > 0:
            if not allow_duplicate_name:
                raise Exception(
                    f"You already have a collection under the name '{name}'. "
                    f"Use --allow-duplicate-name flag to override."
                )

        claim = Claim()
        claim.collection.update(claims=claims, **kwargs)
        tx = await Transaction.claim_create(
            name, claim, amount, claim_address, funding_accounts, funding_accounts[0], channel
        )
        new_txo = tx.outputs[0]

        if channel:
            new_txo.sign(channel)
        await tx.sign(funding_accounts)

        if not preview:
            await self.broadcast_or_release(tx, blocking)
            self.component_manager.loop.create_task(self.analytics_manager.send_claim_action('publish'))
        else:
            await account.ledger.release_tx(tx)

        return tx