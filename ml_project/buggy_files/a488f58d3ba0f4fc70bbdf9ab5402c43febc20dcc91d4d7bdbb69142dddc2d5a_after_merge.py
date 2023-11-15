    def close(self):
        if self.opened:
            try:
                self.dbb_hid.close()
            except:
                pass
        self.opened = False