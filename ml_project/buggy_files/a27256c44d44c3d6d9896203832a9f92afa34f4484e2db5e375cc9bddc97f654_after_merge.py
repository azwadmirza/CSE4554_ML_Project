    def close(self):
        # close the HID device (so can be reused)
        self.dev.close()
        self.dev = None