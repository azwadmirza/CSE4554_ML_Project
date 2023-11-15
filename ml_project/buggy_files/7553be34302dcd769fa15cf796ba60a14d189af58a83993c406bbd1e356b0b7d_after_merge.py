    def _scan_devices_with_hid(self) -> List['Device']:
        try:
            import hid
        except ImportError:
            return []

        devices = []
        for d in hid.enumerate(0, 0):
            product_key = (d['vendor_id'], d['product_id'])
            if product_key in self._recognised_hardware:
                plugin = self._recognised_hardware[product_key]
                device = plugin.create_device_from_hid_enumeration(d, product_key=product_key)
                devices.append(device)
        return devices