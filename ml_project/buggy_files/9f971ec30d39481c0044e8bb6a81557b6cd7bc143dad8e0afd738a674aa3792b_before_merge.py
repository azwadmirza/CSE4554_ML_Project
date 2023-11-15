    def unpaired_device_infos(self, handler, plugin: 'HW_PluginBase', devices=None,
                              include_failing_clients=False):
        '''Returns a list of DeviceInfo objects: one for each connected,
        unpaired device accepted by the plugin.'''
        if not plugin.libraries_available:
            message = plugin.get_library_not_available_message()
            raise HardwarePluginLibraryUnavailable(message)
        if devices is None:
            devices = self.scan_devices()
        devices = [dev for dev in devices if not self.xpub_by_id(dev.id_)]
        infos = []
        for device in devices:
            if device.product_key not in plugin.DEVICE_IDS:
                continue
            try:
                client = self.create_client(device, handler, plugin)
            except Exception as e:
                self.logger.error(f'failed to create client for {plugin.name} at {device.path}: {repr(e)}')
                if include_failing_clients:
                    infos.append(DeviceInfo(device=device, exception=e))
                continue
            if not client:
                continue
            infos.append(DeviceInfo(device=device,
                                    label=client.label(),
                                    initialized=client.is_initialized()))

        return infos