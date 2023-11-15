    def client_for_keystore(self, plugin: 'HW_PluginBase', handler, keystore: 'Hardware_KeyStore',
                            force_pair: bool) -> Optional['HardwareClientBase']:
        self.logger.info("getting client for keystore")
        if handler is None:
            raise Exception(_("Handler not found for") + ' ' + plugin.name + '\n' + _("A library is probably missing."))
        handler.update_status(False)
        devices = self.scan_devices()
        xpub = keystore.xpub
        derivation = keystore.get_derivation_prefix()
        assert derivation is not None
        client = self.client_by_xpub(plugin, xpub, handler, devices)
        if client is None and force_pair:
            info = self.select_device(plugin, handler, keystore, devices)
            client = self.force_pair_xpub(plugin, handler, info, xpub, derivation)
        if client:
            handler.update_status(True)
        if client:
            keystore.opportunistically_fill_in_missing_info_from_device(client)
        self.logger.info("end client for keystore")
        return client