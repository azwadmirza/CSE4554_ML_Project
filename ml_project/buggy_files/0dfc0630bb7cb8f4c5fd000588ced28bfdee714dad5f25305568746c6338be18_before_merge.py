    def get_dbb_device(self, device):
        with self.device_manager().hid_lock:
            dev = hid.device()
            dev.open_path(device.path)
        return dev