    def scan_devices(self) -> Sequence['Device']:
        self.logger.info("scanning devices...")

        # First see what's connected that we know about
        devices = self._scan_devices_with_hid()

        # Let plugin handlers enumerate devices we don't know about
        with self.lock:
            enumerate_funcs = list(self._enumerate_func)
        for f in enumerate_funcs:
            # custom enumerate functions might use hidapi, so use hid thread to be safe
            new_devices_fut = _hid_executor.submit(f)
            try:
                new_devices = new_devices_fut.result()
            except BaseException as e:
                self.logger.error('custom device enum failed. func {}, error {}'
                                  .format(str(f), repr(e)))
            else:
                devices.extend(new_devices)

        # find out what was disconnected
        pairs = [(dev.path, dev.id_) for dev in devices]
        disconnected_clients = []
        with self.lock:
            connected = {}
            for client, pair in self.clients.items():
                if pair in pairs and client.has_usable_connection_with_device():
                    connected[client] = pair
                else:
                    disconnected_clients.append((client, pair[1]))
            self.clients = connected

        # Unpair disconnected devices
        for client, id_ in disconnected_clients:
            self.unpair_id(id_)
            if client.handler:
                client.handler.update_status(False)

        return devices