    def unpaired_device_infos(self, handler: Optional['HardwareHandlerBase'], plugin: 'HW_PluginBase',
                              devices: List['Device'] = None,
                              include_failing_clients=False) -> List['DeviceInfo']:
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
                    infos.append(DeviceInfo(device=device, exception=e, plugin_name=plugin.name))
                continue
            if not client:
                continue
            infos.append(DeviceInfo(device=device,
                                    label=client.label(),
                                    initialized=client.is_initialized(),
                                    plugin_name=plugin.name,
                                    soft_device_id=client.get_soft_device_id()))

        return infos