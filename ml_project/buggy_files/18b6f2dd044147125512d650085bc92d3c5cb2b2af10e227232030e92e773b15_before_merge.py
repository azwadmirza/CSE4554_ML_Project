    async def jsonrpc_collection_update(
            self, claim_id, bid=None,
            channel_id=None, channel_name=None, channel_account_id=None, clear_channel=False,
            account_id=None, wallet_id=None, claim_address=None, funding_account_ids=None,
            preview=False, blocking=False, replace=False, **kwargs):
        """
        Update an existing collection claim.

        Usage:
            collection_update (<claim_id> | --claim_id=<claim_id>) [--bid=<bid>]
                            [--claims=<claims>...] [--clear_claims]
                           [--title=<title>] [--description=<description>]
                           [--tags=<tags>...] [--clear_tags]
                           [--languages=<languages>...] [--clear_languages]
                           [--locations=<locations>...] [--clear_locations]
                           [--thumbnail_url=<thumbnail_url>] [--cover_url=<cover_url>]
                           [--account_id=<account_id>] [--wallet_id=<wallet_id>]
                           [--claim_address=<claim_address>] [--new_signing_key]
                           [--funding_account_ids=<funding_account_ids>...]
                           [--preview] [--blocking] [--replace]

        Options:
            --claim_id=<claim_id>          : (str) claim_id of the collection to update
            --bid=<bid>                    : (decimal) amount to back the claim
            --claims=<claims>              : (list) claim ids
            --clear_claims                 : (bool) clear existing claim references (prior to adding new ones)
            --title=<title>                : (str) title of the collection
            --description=<description>    : (str) description of the collection
            --tags=<tags>                  : (list) add content tags
            --clear_tags                   : (bool) clear existing tags (prior to adding new ones)
            --languages=<languages>        : (list) languages used by the collection,
                                                    using RFC 5646 format, eg:
                                                    for English `--languages=en`
                                                    for Spanish (Spain) `--languages=es-ES`
                                                    for Spanish (Mexican) `--languages=es-MX`
                                                    for Chinese (Simplified) `--languages=zh-Hans`
                                                    for Chinese (Traditional) `--languages=zh-Hant`
            --clear_languages              : (bool) clear existing languages (prior to adding new ones)
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

            --clear_locations              : (bool) clear existing locations (prior to adding new ones)
            --thumbnail_url=<thumbnail_url>: (str) thumbnail url
            --account_id=<account_id>      : (str) account in which to look for collection (default: all)
            --wallet_id=<wallet_id>        : (str) restrict operation to specific wallet
          --funding_account_ids=<funding_account_ids>: (list) ids of accounts to fund this transaction
            --claim_address=<claim_address>: (str) address where the collection is sent
            --new_signing_key              : (bool) generate a new signing key, will invalidate all previous publishes
            --preview                      : (bool) do not broadcast the transaction
            --blocking                     : (bool) wait until transaction is in mempool
            --replace                      : (bool) instead of modifying specific values on
                                                    the collection, this will clear all existing values
                                                    and only save passed in values, useful for form
                                                    submissions where all values are always set

        Returns: {Transaction}
        """
        wallet = self.wallet_manager.get_wallet_or_default(wallet_id)
        funding_accounts = wallet.get_accounts_or_all(funding_account_ids)
        if account_id:
            account = wallet.get_account_or_error(account_id)
            accounts = [account]
        else:
            account = wallet.default_account
            accounts = wallet.accounts

        existing_collections = await self.ledger.get_collections(
            wallet=wallet, accounts=accounts, claim_id=claim_id
        )
        if len(existing_collections) != 1:
            account_ids = ', '.join(f"'{account.id}'" for account in accounts)
            raise Exception(
                f"Can't find the collection '{claim_id}' in account(s) {account_ids}."
            )
        old_txo = existing_collections[0]
        if not old_txo.claim.is_collection:
            raise Exception(
                f"A claim with id '{claim_id}' was found but it is not a collection."
            )

        if bid is not None:
            amount = self.get_dewies_or_error('bid', bid, positive_value=True)
        else:
            amount = old_txo.amount

        if claim_address is not None:
            self.valid_address_or_error(claim_address)
        else:
            claim_address = old_txo.get_address(account.ledger)

        channel = None
        if channel_id or channel_name:
            channel = await self.get_channel_or_error(
                wallet, channel_account_id, channel_id, channel_name, for_signing=True)
        elif old_txo.claim.is_signed and not clear_channel and not replace:
            channel = old_txo.channel

        if replace:
            claim = Claim()
            claim.collection.message.source.CopyFrom(
                old_txo.claim.collection.message.source
            )
            claim.collection.update(**kwargs)
        else:
            claim = Claim.from_bytes(old_txo.claim.to_bytes())
            claim.collection.update(**kwargs)
        tx = await Transaction.claim_update(
            old_txo, claim, amount, claim_address, funding_accounts, funding_accounts[0], channel
        )
        new_txo = tx.outputs[0]

        new_txo.script.generate()

        if channel:
            new_txo.sign(channel)
        await tx.sign(funding_accounts)

        if not preview:
            await self.broadcast_or_release(tx, blocking)
            await self.analytics_manager.send_claim_action('publish')
        else:
            await account.ledger.release_tx(tx)

        return tx