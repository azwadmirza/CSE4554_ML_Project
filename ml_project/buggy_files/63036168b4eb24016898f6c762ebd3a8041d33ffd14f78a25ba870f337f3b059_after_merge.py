    def on_hw_derivation(self, name, device_info: 'DeviceInfo', derivation, xtype):
        from .keystore import hardware_keystore
        devmgr = self.plugins.device_manager
        try:
            xpub = self.plugin.get_xpub(device_info.device.id_, derivation, xtype, self)
            client = devmgr.client_by_id(device_info.device.id_)
            if not client: raise Exception("failed to find client for device id")
            root_fingerprint = client.request_root_fingerprint_from_device()
            label = client.label()  # use this as device_info.label might be outdated!
        except ScriptTypeNotSupported:
            raise  # this is handled in derivation_dialog
        except BaseException as e:
            self.logger.exception('')
            self.show_error(e)
            return
        d = {
            'type': 'hardware',
            'hw_type': name,
            'derivation': derivation,
            'root_fingerprint': root_fingerprint,
            'xpub': xpub,
            'label': label,
        }
        k = hardware_keystore(d)
        self.on_keystore(k)