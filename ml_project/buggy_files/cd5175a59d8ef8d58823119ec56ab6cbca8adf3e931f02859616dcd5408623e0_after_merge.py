    def write(self, string):
        if not string.endswith('\r'):
            string += '\r'
        self.serialPortOrig.write(string.encode())
        self.serialPortOrig.flush()