    def close(self):
        with self.device_manager().hid_lock:
            try:
                self.bitbox02_device.close()
            except:
                pass