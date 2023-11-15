    def close(self):
        with self.device_manager().hid_lock:
            self.dongleObject.dongle.close()