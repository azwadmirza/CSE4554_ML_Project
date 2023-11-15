    def force_pair_xpub(self, plugin: 'HW_PluginBase', handler: 'HardwareHandlerBase',
                        info: 'DeviceInfo', xpub, derivation) -> Optional['HardwareClientBase']:
        # The wallet has not been previously paired, so let the user
        # choose an unpaired device and compare its first address.
        xtype = bip32.xpub_type(xpub)
        client = self.client_lookup(info.device.id_)
        if client and client.is_pairable():
            # See comment above for same code
            client.handler = handler
            # This will trigger a PIN/passphrase entry request
            try:
                client_xpub = client.get_xpub(derivation, xtype)
            except (UserCancelled, RuntimeError):
                 # Bad / cancelled PIN / passphrase
                client_xpub = None
            if client_xpub == xpub:
                self.pair_xpub(xpub, info.device.id_)
                return client

        # The user input has wrong PIN or passphrase, or cancelled input,
        # or it is not pairable
        raise DeviceUnpairableError(
            _('Electrum cannot pair with your {}.\n\n'
              'Before you request bitcoins to be sent to addresses in this '
              'wallet, ensure you can pair with your device, or that you have '
              'its seed (and passphrase, if any).  Otherwise all bitcoins you '
              'receive will be unspendable.').format(plugin.device))