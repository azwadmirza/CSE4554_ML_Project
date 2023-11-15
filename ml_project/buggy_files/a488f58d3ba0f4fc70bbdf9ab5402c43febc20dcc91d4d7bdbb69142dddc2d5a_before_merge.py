    def close(self):
        if self.opened:
            with self.device_manager().hid_lock:
                try:
                    self.dbb_hid.close()
                except:
                    pass
        self.opened = False