    async def jsonrpc_channel_create(
            self, name, bid, allow_duplicate_name=False, account_id=None, wallet_id=None,
            claim_address=None, funding_account_ids=None, preview=False, blocking=False, **kwargs):
        """
        Create a new channel by generating a channel private key and establishing an '@' prefixed claim.

        Usage:
            channel_create (<name> | --name=<name>) (<bid> | --bid=<bid>)
                           [--allow_duplicate_name=<allow_duplicate_name>]
                           [--title=<title>] [--description=<description>] [--email=<email>]
                           [--website_url=<website_url>] [--featured=<featured>...]
                           [--tags=<tags>...] [--languages=<languages>...] [--locations=<locations>...]
                           [--thumbnail_url=<thumbnail_url>] [--cover_url=<cover_url>]
                           [--account_id=<account_id>] [--wallet_id=<wallet_id>]
                           [--claim_address=<claim_address>] [--funding_account_ids=<funding_account_ids>...]
                           [--preview] [--blocking]

        Options:
            --name=<name>                  : (str) name of the channel prefixed with '@'
            --bid=<bid>                    : (decimal) amount to back the claim
        --allow_duplicate_name=<allow_duplicate_name> : (bool) create new channel even if one already exists with
                                              given name. default: false.
            --title=<title>                : (str) title of the publication
            --description=<description>    : (str) description of the publication
            --email=<email>                : (str) email of channel owner
            --website_url=<website_url>    : (str) website url
            --featured=<featured>          : (list) claim_ids of featured content in channel
            --tags=<tags>                  : (list) content tags
            --languages=<languages>        : (list) languages used by the channel,
                                                    using RFC 5646 format, eg:
                                                    for English `--languages=en`
                                                    for Spanish (Spain) `--languages=es-ES`
                                                    for Spanish (Mexican) `--languages=es-MX`
                                                    for Chinese (Simplified) `--languages=zh-Hans`
                                                    for Chinese (Traditional) `--languages=zh-Hant`
            --locations=<locations>        : (list) locations of the channel, consisting of 2 letter
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
            --cover_url=<cover_url>        : (str) url of cover image
            --account_id=<account_id>      : (str) account to use for holding the transaction
            --wallet_id=<wallet_id>        : (str) restrict operation to specific wallet
          --funding_account_ids=<funding_account_ids>: (list) ids of accounts to fund this transaction
            --claim_address=<claim_address>: (str) address where the channel is sent to, if not specified
                                                   it will be determined automatically from the account
            --preview                      : (bool) do not broadcast the transaction
            --blocking                     : (bool) wait until transaction is in mempool

        Returns: {Transaction}
        """
        wallet = self.wallet_manager.get_wallet_or_default(wallet_id)
        assert not wallet.is_locked, "Cannot spend funds with locked wallet, unlock first."
        account = wallet.get_account_or_default(account_id)
        funding_accounts = wallet.get_accounts_or_all(funding_account_ids)
        self.valid_channel_name_or_error(name)
        amount = self.get_dewies_or_error('bid', bid, positive_value=True)
        claim_address = await self.get_receiving_address(claim_address, account)

        existing_channels = await self.ledger.get_channels(accounts=wallet.accounts, claim_name=name)
        if len(existing_channels) > 0:
            if not allow_duplicate_name:
                raise Exception(
                    f"You already have a channel under the name '{name}'. "
                    f"Use --allow-duplicate-name flag to override."
                )

        claim = Claim()
        claim.channel.update(**kwargs)
        tx = await Transaction.claim_create(
            name, claim, amount, claim_address, funding_accounts, funding_accounts[0]
        )
        txo = tx.outputs[0]
        txo.generate_channel_private_key()

        await tx.sign(funding_accounts)

        if not preview:
            account.add_channel_private_key(txo.private_key)
            wallet.save()
            await self.broadcast_or_release(tx, blocking)
            await self.storage.save_claims([self._old_get_temp_claim_info(
                tx, txo, claim_address, claim, name, dewies_to_lbc(amount)
            )])
            await self.analytics_manager.send_new_channel()
        else:
            await account.ledger.release_tx(tx)

        return tx