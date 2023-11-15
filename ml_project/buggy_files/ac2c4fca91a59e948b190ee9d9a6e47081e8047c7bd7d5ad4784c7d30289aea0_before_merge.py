    async def jsonrpc_channel_update(
            self, claim_id, bid=None, account_id=None, wallet_id=None, claim_address=None,
            funding_account_ids=None, new_signing_key=False, preview=False,
            blocking=False, replace=False, **kwargs):
        """
        Update an existing channel claim.

        Usage:
            channel_update (<claim_id> | --claim_id=<claim_id>) [<bid> | --bid=<bid>]
                           [--title=<title>] [--description=<description>] [--email=<email>]
                           [--website_url=<website_url>]
                           [--featured=<featured>...] [--clear_featured]
                           [--tags=<tags>...] [--clear_tags]
                           [--languages=<languages>...] [--clear_languages]
                           [--locations=<locations>...] [--clear_locations]
                           [--thumbnail_url=<thumbnail_url>] [--cover_url=<cover_url>]
                           [--account_id=<account_id>] [--wallet_id=<wallet_id>]
                           [--claim_address=<claim_address>] [--new_signing_key]
                           [--funding_account_ids=<funding_account_ids>...]
                           [--preview] [--blocking] [--replace]

        Options:
            --claim_id=<claim_id>          : (str) claim_id of the channel to update
            --bid=<bid>                    : (decimal) amount to back the claim
            --title=<title>                : (str) title of the publication
            --description=<description>    : (str) description of the publication
            --email=<email>                : (str) email of channel owner
            --website_url=<website_url>    : (str) website url
            --featured=<featured>          : (list) claim_ids of featured content in channel
            --clear_featured               : (bool) clear existing featured content (prior to adding new ones)
            --tags=<tags>                  : (list) add content tags
            --clear_tags                   : (bool) clear existing tags (prior to adding new ones)
            --languages=<languages>        : (list) languages used by the channel,
                                                    using RFC 5646 format, eg:
                                                    for English `--languages=en`
                                                    for Spanish (Spain) `--languages=es-ES`
                                                    for Spanish (Mexican) `--languages=es-MX`
                                                    for Chinese (Simplified) `--languages=zh-Hans`
                                                    for Chinese (Traditional) `--languages=zh-Hant`
            --clear_languages              : (bool) clear existing languages (prior to adding new ones)
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

            --clear_locations              : (bool) clear existing locations (prior to adding new ones)
            --thumbnail_url=<thumbnail_url>: (str) thumbnail url
            --cover_url=<cover_url>        : (str) url of cover image
            --account_id=<account_id>      : (str) account in which to look for channel (default: all)
            --wallet_id=<wallet_id>        : (str) restrict operation to specific wallet
          --funding_account_ids=<funding_account_ids>: (list) ids of accounts to fund this transaction
            --claim_address=<claim_address>: (str) address where the channel is sent
            --new_signing_key              : (bool) generate a new signing key, will invalidate all previous publishes
            --preview                      : (bool) do not broadcast the transaction
            --blocking                     : (bool) wait until transaction is in mempool
            --replace                      : (bool) instead of modifying specific values on
                                                    the channel, this will clear all existing values
                                                    and only save passed in values, useful for form
                                                    submissions where all values are always set

        Returns: {Transaction}
        """
        wallet = self.wallet_manager.get_wallet_or_default(wallet_id)
        assert not wallet.is_locked, "Cannot spend funds with locked wallet, unlock first."
        funding_accounts = wallet.get_accounts_or_all(funding_account_ids)
        if account_id:
            account = wallet.get_account_or_error(account_id)
            accounts = [account]
        else:
            account = wallet.default_account
            accounts = wallet.accounts

        existing_channels = await self.ledger.get_claims(
            wallet=wallet, accounts=accounts, claim_id=claim_id
        )
        if len(existing_channels) != 1:
            account_ids = ', '.join(f"'{account.id}'" for account in accounts)
            raise Exception(
                f"Can't find the channel '{claim_id}' in account(s) {account_ids}."
            )
        old_txo = existing_channels[0]
        if not old_txo.claim.is_channel:
            raise Exception(
                f"A claim with id '{claim_id}' was found but it is not a channel."
            )

        if bid is not None:
            amount = self.get_dewies_or_error('bid', bid, positive_value=True)
        else:
            amount = old_txo.amount

        if claim_address is not None:
            self.valid_address_or_error(claim_address)
        else:
            claim_address = old_txo.get_address(account.ledger)

        if replace:
            claim = Claim()
            claim.channel.public_key_bytes = old_txo.claim.channel.public_key_bytes
        else:
            claim = Claim.from_bytes(old_txo.claim.to_bytes())
        claim.channel.update(**kwargs)
        tx = await Transaction.claim_update(
            old_txo, claim, amount, claim_address, funding_accounts, funding_accounts[0]
        )
        new_txo = tx.outputs[0]

        if new_signing_key:
            new_txo.generate_channel_private_key()
        else:
            new_txo.private_key = old_txo.private_key

        new_txo.script.generate()

        await tx.sign(funding_accounts)

        if not preview:
            account.add_channel_private_key(new_txo.private_key)
            wallet.save()
            await self.broadcast_or_release(tx, blocking)
            await self.storage.save_claims([self._old_get_temp_claim_info(
                tx, new_txo, claim_address, new_txo.claim, new_txo.claim_name, dewies_to_lbc(amount)
            )])
            await self.analytics_manager.send_new_channel()
        else:
            await account.ledger.release_tx(tx)

        return tx