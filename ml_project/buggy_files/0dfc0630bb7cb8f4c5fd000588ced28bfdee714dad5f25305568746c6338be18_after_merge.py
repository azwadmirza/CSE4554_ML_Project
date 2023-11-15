    def get_dbb_device(self, device):
        dev = hid.device()
        dev.open_path(device.path)
        return dev