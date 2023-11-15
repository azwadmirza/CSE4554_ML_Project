    def repr(self):
        if self.target == self.alias:
            return self.target
        return '{s.target}:{s.alias}'.format(s=self)