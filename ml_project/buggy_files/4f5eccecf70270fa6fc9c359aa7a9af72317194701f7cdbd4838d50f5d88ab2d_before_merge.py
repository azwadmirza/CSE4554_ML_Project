    def client_by_xpub(self, plugin: 'HW_PluginBase', xpub, handler,
                       devices: Iterable['Device']) -> Optional['HardwareClientBase']:
        _id = self.xpub_id(xpub)
        client = self.client_lookup(_id)
        if client:
            # An unpaired client might have another wallet's handler
            # from a prior scan.  Replace to fix dialog parenting.
            client.handler = handler
            return client

        for device in devices:
            if device.id_ == _id:
                return self.create_client(device, handler, plugin)