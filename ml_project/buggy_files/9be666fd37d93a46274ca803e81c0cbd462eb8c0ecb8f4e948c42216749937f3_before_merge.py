    def write(self, val):
        self.process.stdin.write(str(val))
        self.process.stdin.flush()