    async def _shutdown(self, chan: Channel, payload, is_local):
        # wait until no HTLCs remain in either commitment transaction
        while len(chan.hm.htlcs(LOCAL)) + len(chan.hm.htlcs(REMOTE)) > 0:
            self.logger.info(f'(chan: {chan.short_channel_id}) waiting for htlcs to settle...')
            await asyncio.sleep(1)
        # if no HTLCs remain, we must not send updates
        chan.set_can_send_ctx_updates(False)
        their_scriptpubkey = payload['scriptpubkey']
        our_scriptpubkey = bfh(bitcoin.address_to_script(chan.sweep_address))
        # estimate fee of closing tx
        our_sig, closing_tx = chan.make_closing_tx(our_scriptpubkey, their_scriptpubkey, fee_sat=0)
        fee_rate = self.network.config.fee_per_kb()
        our_fee = fee_rate * closing_tx.estimated_size() // 1000
        # BOLT2: The sending node MUST set fee less than or equal to the base fee of the final ctx
        max_fee = chan.get_latest_fee(LOCAL if is_local else REMOTE)
        our_fee = min(our_fee, max_fee)
        drop_remote = False
        def send_closing_signed():
            our_sig, closing_tx = chan.make_closing_tx(our_scriptpubkey, their_scriptpubkey, fee_sat=our_fee, drop_remote=drop_remote)
            self.send_message('closing_signed', channel_id=chan.channel_id, fee_satoshis=our_fee, signature=our_sig)
        def verify_signature(tx, sig):
            their_pubkey = chan.config[REMOTE].multisig_key.pubkey
            preimage_hex = tx.serialize_preimage(0)
            pre_hash = sha256d(bfh(preimage_hex))
            return ecc.verify_signature(their_pubkey, sig, pre_hash)
        # the funder sends the first 'closing_signed' message
        if chan.constraints.is_initiator:
            send_closing_signed()
        # negotiate fee
        while True:
            # FIXME: the remote SHOULD send closing_signed, but some don't.
            cs_payload = await self.wait_for_message('closing_signed', chan.channel_id)
            their_fee = cs_payload['fee_satoshis']
            if their_fee > max_fee:
                raise Exception(f'the proposed fee exceeds the base fee of the latest commitment transaction {is_local, their_fee, max_fee}')
            their_sig = cs_payload['signature']
            # verify their sig: they might have dropped their output
            our_sig, closing_tx = chan.make_closing_tx(our_scriptpubkey, their_scriptpubkey, fee_sat=their_fee, drop_remote=False)
            if verify_signature(closing_tx, their_sig):
                drop_remote = False
            else:
                our_sig, closing_tx = chan.make_closing_tx(our_scriptpubkey, their_scriptpubkey, fee_sat=their_fee, drop_remote=True)
                if verify_signature(closing_tx, their_sig):
                    drop_remote = True
                else:
                    raise Exception('failed to verify their signature')
            # Agree if difference is lower or equal to one (see below)
            if abs(our_fee - their_fee) < 2:
                our_fee = their_fee
                break
            # this will be "strictly between" (as in BOLT2) previous values because of the above
            our_fee = (our_fee + their_fee) // 2
            # another round
            send_closing_signed()
        # the non-funder replies
        if not chan.constraints.is_initiator:
            send_closing_signed()
        # add signatures
        closing_tx.add_signature_to_txin(
            txin_idx=0,
            signing_pubkey=chan.config[LOCAL].multisig_key.pubkey.hex(),
            sig=bh2u(der_sig_from_sig_string(our_sig) + b'\x01'))
        closing_tx.add_signature_to_txin(
            txin_idx=0,
            signing_pubkey=chan.config[REMOTE].multisig_key.pubkey.hex(),
            sig=bh2u(der_sig_from_sig_string(their_sig) + b'\x01'))
        # save local transaction and set state
        try:
            self.lnworker.wallet.add_transaction(closing_tx)
        except UnrelatedTransactionException:
            pass  # this can happen if (~all the balance goes to REMOTE)
        chan.set_state(ChannelState.CLOSING)
        # broadcast
        await self.network.try_broadcasting(closing_tx, 'closing')
        return closing_tx.txid()