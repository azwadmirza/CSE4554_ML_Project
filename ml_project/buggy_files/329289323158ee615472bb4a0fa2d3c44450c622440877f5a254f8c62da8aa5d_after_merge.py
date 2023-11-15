    def _query_blockchain_balances(
            self,
            blockchain: Optional[SupportedBlockchain],
            ignore_cache: bool,
    ) -> Dict[str, Any]:
        msg = ''
        status_code = HTTPStatus.OK
        result = None
        try:
            balances = self.rotkehlchen.chain_manager.query_balances(
                blockchain=blockchain,
                ignore_cache=ignore_cache,
            )
        except EthSyncError as e:
            msg = str(e)
            status_code = HTTPStatus.CONFLICT
        except RemoteError as e:
            msg = str(e)
            status_code = HTTPStatus.BAD_GATEWAY
        else:
            result = balances.serialize()
            # If only specific input blockchain was given ignore other results
            if blockchain == SupportedBlockchain.ETHEREUM:
                result['per_account'].pop('BTC', None)
                result['totals'].pop('BTC', None)
            elif blockchain == SupportedBlockchain.BITCOIN:
                val = result['per_account'].get('BTC', None)
                per_account = {'BTC': val} if val else {}
                val = result['totals'].get('BTC', None)
                totals = {'BTC': val} if val else {}
                result = {'per_account': per_account, 'totals': totals}

        return {'result': result, 'message': msg, 'status_code': status_code}