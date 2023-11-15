    def clear(self, nomove=False):
        """
        Clear current bar display
        """
        if self.disable:
            return

        if not nomove:
            self.moveto(self.pos)
        # clear up the bar (can't rely on sp(''))
        self.fp.write('\r')
        self.fp.write(' ' * (self.ncols if self.ncols else 10))
        self.fp.write('\r')  # place cursor back at the beginning of line
        if not nomove:
            self.moveto(-self.pos)