    def write(self, val):
        self.process.stdin.write(utf8bytes(str(val)))
        self.process.stdin.flush()