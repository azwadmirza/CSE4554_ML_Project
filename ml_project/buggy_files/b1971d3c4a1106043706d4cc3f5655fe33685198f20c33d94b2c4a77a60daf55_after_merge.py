    async def jsonrpc_stream_create(
            self, name, bid, file_path, allow_duplicate_name=False,
            channel_id=None, channel_name=None, channel_account_id=None,
            account_id=None, wallet_id=None, claim_address=None, funding_account_ids=None,
            preview=False, blocking=False, validate_file=False, optimize_file=False, **kwargs):
        """
        Make a new stream claim and announce the associated file to lbrynet.

        Usage:
            stream_create (<name> | --name=<name>) (<bid> | --bid=<bid>) (<file_path> | --file_path=<file_path>)
                    [--validate_file] [--optimize_file]
                    [--allow_duplicate_name=<allow_duplicate_name>]
                    [--fee_currency=<fee_currency>] [--fee_amount=<fee_amount>] [--fee_address=<fee_address>]
                    [--title=<title>] [--description=<description>] [--author=<author>]
                    [--tags=<tags>...] [--languages=<languages>...] [--locations=<locations>...]
                    [--license=<license>] [--license_url=<license_url>] [--thumbnail_url=<thumbnail_url>]
                    [--release_time=<release_time>] [--width=<width>] [--height=<height>] [--duration=<duration>]
                    [--channel_id=<channel_id> | --channel_name=<channel_name>]
                    [--channel_account_id=<channel_account_id>...]
                    [--account_id=<account_id>] [--wallet_id=<wallet_id>]
                    [--claim_address=<claim_address>] [--funding_account_ids=<funding_account_ids>...]
                    [--preview] [--blocking]

        Options:
            --name=<name>                  : (str) name of the content (can only consist of a-z A-Z 0-9 and -(dash))
            --bid=<bid>                    : (decimal) amount to back the claim
            --file_path=<file_path>        : (str) path to file to be associated with name.
            --validate_file                : (bool) validate that the video container and encodings match
                                             common web browser support or that optimization succeeds if specified.
                                             FFmpeg is required
            --optimize_file                : (bool) transcode the video & audio if necessary to ensure
                                             common web browser support. FFmpeg is required
        --allow_duplicate_name=<allow_duplicate_name> : (bool) create new claim even if one already exists with
                                              given name. default: false.
            --fee_currency=<fee_currency>  : (string) specify fee currency
            --fee_amount=<fee_amount>      : (decimal) content download fee
            --fee_address=<fee_address>    : (str) address where to send fee payments, will use
                                                   value from --claim_address if not provided
            --title=<title>                : (str) title of the publication
            --description=<description>    : (str) description of the publication
            --author=<author>              : (str) author of the publication. The usage for this field is not
                                             the same as for channels. The author field is used to credit an author
                                             who is not the publisher and is not represented by the channel. For
                                             example, a pdf file of 'The Odyssey' has an author of 'Homer' but may
                                             by published to a channel such as '@classics', or to no channel at all
            --tags=<tags>                  : (list) add content tags
            --languages=<languages>        : (list) languages used by the channel,
                                                    using RFC 5646 format, eg:
                                                    for English `--languages=en`
                                                    for Spanish (Spain) `--languages=es-ES`
                                                    for Spanish (Mexican) `--languages=es-MX`
                                                    for Chinese (Simplified) `--languages=zh-Hans`
                                                    for Chinese (Traditional) `--languages=zh-Hant`
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

            --license=<license>            : (str) publication license
            --license_url=<license_url>    : (str) publication license url
            --thumbnail_url=<thumbnail_url>: (str) thumbnail url
            --release_time=<release_time>  : (int) original public release of content, seconds since UNIX epoch
            --width=<width>                : (int) image/video width, automatically calculated from media file
            --height=<height>              : (int) image/video height, automatically calculated from media file
            --duration=<duration>          : (int) audio/video duration in seconds, automatically calculated
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
        assert not wallet.is_locked, "Cannot spend funds with locked wallet, unlock first."
        self.valid_stream_name_or_error(name)
        account = wallet.get_account_or_default(account_id)
        funding_accounts = wallet.get_accounts_or_all(funding_account_ids)
        channel = await self.get_channel_or_none(wallet, channel_account_id, channel_id, channel_name, for_signing=True)
        amount = self.get_dewies_or_error('bid', bid, positive_value=True)
        claim_address = await self.get_receiving_address(claim_address, account)
        kwargs['fee_address'] = self.get_fee_address(kwargs, claim_address)

        claims = await account.get_claims(claim_name=name)
        if len(claims) > 0:
            if not allow_duplicate_name:
                raise Exception(
                    f"You already have a stream claim published under the name '{name}'. "
                    f"Use --allow-duplicate-name flag to override."
                )

        file_path = await self._video_file_analyzer.verify_or_repair(validate_file, optimize_file, file_path)

        claim = Claim()
        claim.stream.update(file_path=file_path, sd_hash='0' * 96, **kwargs)
        tx = await Transaction.claim_create(
            name, claim, amount, claim_address, funding_accounts, funding_accounts[0], channel
        )
        new_txo = tx.outputs[0]

        file_stream = None
        if not preview:
            file_stream = await self.stream_manager.create_stream(file_path)
            claim.stream.source.sd_hash = file_stream.sd_hash
            new_txo.script.generate()

        if channel:
            new_txo.sign(channel)
        await tx.sign(funding_accounts)

        if not preview:
            await self.broadcast_or_release(tx, blocking)
            await self.storage.save_claims([self._old_get_temp_claim_info(
                tx, new_txo, claim_address, claim, name, dewies_to_lbc(amount)
            )])
            await self.storage.save_content_claim(file_stream.stream_hash, new_txo.id)
            self.component_manager.loop.create_task(self.analytics_manager.send_claim_action('publish'))
        else:
            await account.ledger.release_tx(tx)

        return tx