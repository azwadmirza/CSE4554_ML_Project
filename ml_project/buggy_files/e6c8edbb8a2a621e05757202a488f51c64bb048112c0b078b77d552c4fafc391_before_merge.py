    def close(self):
        for stream in [self.process.stdin, self.process.stdout, self.process.stderr]:
            stream.close()