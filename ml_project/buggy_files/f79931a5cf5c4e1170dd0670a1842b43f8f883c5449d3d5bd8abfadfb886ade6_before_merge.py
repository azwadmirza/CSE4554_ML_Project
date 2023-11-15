    def doit(self):
        if self.args[0].is_zero is False:
            return self.args[0] / Abs(self.args[0])
        return self