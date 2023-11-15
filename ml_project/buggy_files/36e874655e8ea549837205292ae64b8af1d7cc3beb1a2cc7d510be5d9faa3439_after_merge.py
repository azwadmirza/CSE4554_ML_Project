    async def jsonrpc_stream_repost(self, name, bid, claim_id, allow_duplicate_name=False, channel_id=None,
                                    channel_name=None, channel_account_id=None, account_id=None, wallet_id=None,
                                    claim_address=None, funding_account_ids=None, preview=False, blocking=False):
        """
            Creates a claim that references an existing stream by its claim id.

            Usage:
                stream_repost (<name> | --name=<name>) (<bid> | --bid=<bid>) (<claim_id> | --claim_id=<claim_id>)
                        [--allow_duplicate_name=<allow_duplicate_name>]
                        [--channel_id=<channel_id> | --channel_name=<channel_name>]
                        [--channel_account_id=<channel_account_id>...]
                        [--account_id=<account_id>] [--wallet_id=<wallet_id>]
                        [--claim_address=<claim_address>] [--funding_account_ids=<funding_account_ids>...]
                        [--preview] [--blocking]

            Options:
                --name=<name>                  : (str) name of the content (can only consist of a-z A-Z 0-9 and -(dash))
                --bid=<bid>                    : (decimal) amount to back the claim
                --claim_id=<claim_id>          : (str) id of the claim being reposted
                --allow_duplicate_name=<allow_duplicate_name> : (bool) create new claim even if one already exists with
                                                                       given name. default: false.
                --channel_id=<channel_id>      : (str) claim id of the publisher channel
                --channel_name=<channel_name>  : (str) name of the publisher channel
                --channel_account_id=<channel_account_id>: (str) one or more account ids for accounts to look in
                                                                 for channel certificates, defaults to all accounts.
                --account_id=<account_id>      : (str) account to use for holding the transaction
                --wallet_id=<wallet_id>        : (str) restrict operation to specific wallet
                --funding_account_ids=<funding_account_ids>: (list) ids of accounts to fund this transaction
                --claim_address=<claim_address>: (str) address where the claim is sent to, if not specified
                                                       it will be determined automatically from the account
                --preview                      : (bool) do not broadcast the transaction
                --blocking                     : (bool) wait until transaction is in mempool

            Returns: {Transaction}
            """
        wallet = self.wallet_manager.get_wallet_or_default(wallet_id)
        self.valid_stream_name_or_error(name)
        account = wallet.get_account_or_default(account_id)
        funding_accounts = wallet.get_accounts_or_all(funding_account_ids)
        channel = await self.get_channel_or_none(wallet, channel_account_id, channel_id, channel_name, for_signing=True)
        amount = self.get_dewies_or_error('bid', bid, positive_value=True)
        claim_address = await self.get_receiving_address(claim_address, account)
        claims = await account.get_claims(claim_name=name)
        if len(claims) > 0:
            if not allow_duplicate_name:
                raise Exception(
                    f"You already have a stream claim published under the name '{name}'. "
                    f"Use --allow-duplicate-name flag to override."
                )
        if not VALID_FULL_CLAIM_ID.fullmatch(claim_id):
            raise Exception('Invalid claim id. It is expected to be a 40 characters long hexadecimal string.')

        claim = Claim()
        claim.repost.reference.claim_id = claim_id
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