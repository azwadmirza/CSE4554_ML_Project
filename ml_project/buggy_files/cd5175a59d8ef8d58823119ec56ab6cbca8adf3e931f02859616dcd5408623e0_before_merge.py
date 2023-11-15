    def write(self, string):
        if not string.endswith('\r'):
            string += '\r'
        self.serialPort.write(string.decode())
        self.serialPort.flush()