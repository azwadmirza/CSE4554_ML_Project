    def write(self, s):
        """Writes data to the original std stream and the in-memory object."""
        std_s = s
        if self.prestd:
            std_s = self.prestd + std_s
        if self.poststd:
            std_s += self.poststd
        self.std.write(std_s)
        self.mem.write(s)