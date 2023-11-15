    def close(self):
        # close the HID device (so can be reused)
        with self.device_manager().hid_lock:
            self.dev.close()
        self.dev = None