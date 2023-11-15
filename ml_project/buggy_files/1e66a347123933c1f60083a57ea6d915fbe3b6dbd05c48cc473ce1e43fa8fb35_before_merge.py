    async def jsonrpc_stream_update(
            self, claim_id, bid=None, file_path=None,
            channel_id=None, channel_name=None, channel_account_id=None, clear_channel=False,
            account_id=None, wallet_id=None, claim_address=None, funding_account_ids=None,
            preview=False, blocking=False, replace=False, **kwargs):
        """
        Update an existing stream claim and if a new file is provided announce it to lbrynet.

        Usage:
            stream_update (<claim_id> | --claim_id=<claim_id>) [--bid=<bid>] [--file_path=<file_path>]
                    [--file_name=<file_name>] [--file_size=<file_size>] [--file_hash=<file_hash>]
                    [--fee_currency=<fee_currency>] [--fee_amount=<fee_amount>]
                    [--fee_address=<fee_address>] [--clear_fee]
                    [--title=<title>] [--description=<description>] [--author=<author>]
                    [--tags=<tags>...] [--clear_tags]
                    [--languages=<languages>...] [--clear_languages]
                    [--locations=<locations>...] [--clear_locations]
                    [--license=<license>] [--license_url=<license_url>] [--thumbnail_url=<thumbnail_url>]
                    [--release_time=<release_time>] [--width=<width>] [--height=<height>] [--duration=<duration>]
                    [--channel_id=<channel_id> | --channel_name=<channel_name> | --clear_channel]
                    [--channel_account_id=<channel_account_id>...]
                    [--account_id=<account_id>] [--wallet_id=<wallet_id>]
                    [--claim_address=<claim_address>] [--funding_account_ids=<funding_account_ids>...]
                    [--preview] [--blocking] [--replace]

        Options:
            --claim_id=<claim_id>          : (str) id of the stream claim to update
            --bid=<bid>                    : (decimal) amount to back the claim
            --file_path=<file_path>        : (str) path to file to be associated with name.
            --file_name=<file_name>        : (str) override file name, defaults to name from file_path.
            --file_size=<file_size>        : (str) override file size, otherwise automatically computed.
            --file_hash=<file_hash>        : (str) override file hash, otherwise automatically computed.
            --fee_currency=<fee_currency>  : (string) specify fee currency
            --fee_amount=<fee_amount>      : (decimal) content download fee
            --fee_address=<fee_address>    : (str) address where to send fee payments, will use
                                                   value from --claim_address if not provided
            --clear_fee                    : (bool) clear previously set fee
            --title=<title>                : (str) title of the publication
            --description=<description>    : (str) description of the publication
            --author=<author>              : (str) author of the publication. The usage for this field is not
                                             the same as for channels. The author field is used to credit an author
                                             who is not the publisher and is not represented by the channel. For
                                             example, a pdf file of 'The Odyssey' has an author of 'Homer' but may
                                             by published to a channel such as '@classics', or to no channel at all
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
            --locations=<locations>        : (list) locations relevant to the stream, consisting of 2 letter
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
            --license=<license>            : (str) publication license
            --license_url=<license_url>    : (str) publication license url
            --thumbnail_url=<thumbnail_url>: (str) thumbnail url
            --release_time=<release_time>  : (int) original public release of content, seconds since UNIX epoch
            --width=<width>                : (int) image/video width, automatically calculated from media file
            --height=<height>              : (int) image/video height, automatically calculated from media file
            --duration=<duration>          : (int) audio/video duration in seconds, automatically calculated
            --channel_id=<channel_id>      : (str) claim id of the publisher channel
            --channel_name=<channel_name>  : (str) name of the publisher channel
            --clear_channel                : (bool) remove channel signature
          --channel_account_id=<channel_account_id>: (str) one or more account ids for accounts to look in
                                                   for channel certificates, defaults to all accounts.
            --account_id=<account_id>      : (str) account in which to look for stream (default: all)
            --wallet_id=<wallet_id>        : (str) restrict operation to specific wallet
          --funding_account_ids=<funding_account_ids>: (list) ids of accounts to fund this transaction
            --claim_address=<claim_address>: (str) address where the claim is sent to, if not specified
                                                   it will be determined automatically from the account
            --preview                      : (bool) do not broadcast the transaction
            --blocking                     : (bool) wait until transaction is in mempool
            --replace                      : (bool) instead of modifying specific values on
                                                    the stream, this will clear all existing values
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

        existing_claims = await self.ledger.get_claims(
            wallet=wallet, accounts=accounts, claim_id=claim_id
        )
        if len(existing_claims) != 1:
            account_ids = ', '.join(f"'{account.id}'" for account in accounts)
            raise Exception(
                f"Can't find the stream '{claim_id}' in account(s) {account_ids}."
            )
        old_txo = existing_claims[0]
        if not old_txo.claim.is_stream:
            raise Exception(
                f"A claim with id '{claim_id}' was found but it is not a stream claim."
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

        fee_address = self.get_fee_address(kwargs, claim_address)
        if fee_address:
            kwargs['fee_address'] = fee_address

        if replace:
            claim = Claim()
            claim.stream.message.source.CopyFrom(
                old_txo.claim.stream.message.source
            )
            stream_type = old_txo.claim.stream.stream_type
            if stream_type:
                old_stream_type = getattr(old_txo.claim.stream.message, stream_type)
                new_stream_type = getattr(claim.stream.message, stream_type)
                new_stream_type.CopyFrom(old_stream_type)
            claim.stream.update(file_path=file_path, **kwargs)
        else:
            claim = Claim.from_bytes(old_txo.claim.to_bytes())
            claim.stream.update(file_path=file_path, **kwargs)
        tx = await Transaction.claim_update(
            old_txo, claim, amount, claim_address, funding_accounts, funding_accounts[0], channel
        )
        new_txo = tx.outputs[0]

        stream_hash = None
        if not preview:
            old_stream_hash = await self.storage.get_stream_hash_for_sd_hash(old_txo.claim.stream.source.sd_hash)
            if file_path is not None:
                if old_stream_hash:
                    stream_to_delete = self.stream_manager.get_stream_by_stream_hash(old_stream_hash)
                    await self.stream_manager.delete_stream(stream_to_delete, delete_file=False)
                file_stream = await self.stream_manager.create_stream(file_path)
                new_txo.claim.stream.source.sd_hash = file_stream.sd_hash
                new_txo.script.generate()
                stream_hash = file_stream.stream_hash
            else:
                stream_hash = old_stream_hash

        if channel:
            new_txo.sign(channel)
        await tx.sign(funding_accounts)

        if not preview:
            await self.broadcast_or_release(tx, blocking)
            await self.storage.save_claims([self._old_get_temp_claim_info(
                tx, new_txo, claim_address, new_txo.claim, new_txo.claim_name, dewies_to_lbc(amount)
            )])
            if stream_hash:
                await self.storage.save_content_claim(stream_hash, new_txo.id)
            await self.analytics_manager.send_claim_action('publish')
        else:
            await account.ledger.release_tx(tx)

        return tx