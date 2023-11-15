    def rpc(self, method, args):
        """ Returns the result of an rpc call to the Bitcoin Core RPC API.
        If the connection is permanently or unrecognizably broken, None
        is returned *and the reactor is shutdown* (because we consider this
        condition unsafe - TODO possibly create a "freeze" mode that could
        restart when the connection is healed, but that is tricky).
        """
        if method not in ['importaddress', 'walletpassphrase', 'getaccount',
                          'gettransaction', 'getrawtransaction', 'gettxout',
                          'importmulti', 'listtransactions', 'getblockcount',
                          'scantxoutset']:
            log.debug('rpc: ' + method + " " + str(args))
        try:
            res = self.jsonRpc.call(method, args)
        except JsonRpcConnectionError as e:
            # note that we only raise this in case the connection error is
            # a refusal, or is unrecognized/unknown by our code. So this does
            # NOT happen in a reset or broken pipe scenario.
            # It is safest to simply shut down.
            # Why not sys.exit? sys.exit calls do *not* work inside delayedCalls
            # or deferreds in twisted, since a bare exception catch prevents
            # an actual system exit (i.e. SystemExit is caught as a
            # BareException type).
            log.error("Failure of RPC connection to Bitcoin Core. "
                      "Application cannot continue, shutting down.")
            if reactor.running:
                reactor.stop()
            return None
        return res