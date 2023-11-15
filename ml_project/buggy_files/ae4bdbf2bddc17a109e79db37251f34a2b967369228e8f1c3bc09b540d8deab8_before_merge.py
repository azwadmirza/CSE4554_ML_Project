    def create_client(self, device: 'Device', handler, plugin: 'HW_PluginBase') -> Optional['HardwareClientBase']:
        # Get from cache first
        client = self.client_lookup(device.id_)
        if client:
            return client
        client = plugin.create_client(device, handler)
        if client:
            self.logger.info(f"Registering {client}")
            with self.lock:
                self.clients[client] = (device.path, device.id_)
        return client