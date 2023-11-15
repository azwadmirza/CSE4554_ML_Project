    def _write(self, data):
        padding = [0x0]*(_WRITE_LENGTH - len(data))
        self.device.write(data + padding)