    def close(self):
        try:
            self.bitbox02_device.close()
        except:
            pass