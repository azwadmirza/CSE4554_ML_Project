    def writeln(self, val):
        self.process.stdin.write(utf8bytes(str(val) + '\n'))
        self.process.stdin.flush()